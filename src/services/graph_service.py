from langchain.chains.conversation.memory import ConversationSummaryBufferMemory
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain_core.messages import trim_messages
from typing_extensions import TypedDict
from typing import Annotated


from langgraph.checkpoint.memory import MemorySaver
import sys

sys.path.insert(0, './src/')

# LLM -----------------------------------------------------

from langchain_core.messages import HumanMessage, SystemMessage, AIMessage

# Our graph is a state machine 

class GraphService:

    class State(TypedDict):
        messages: Annotated[list, add_messages]
        final_prompt: str
        original_prompt: str


    def trim_state_messages(self, messages):
        return trim_messages(messages, strategy="last", include_system=True, max_tokens=1000, start_on="human", token_counter=self.llm)

    def chatbot(self, state):
        original_prompt = state['original_prompt'] # query without injected content. This goes into chat history.
        final_prompt = state['final_prompt']
        trimmed_chat_history = self.trim_state_messages(state['messages'])
        
        return {"messages": trimmed_chat_history + [HumanMessage(original_prompt), self.llm.invoke([self.system_prompt] + trimmed_chat_history + [HumanMessage(final_prompt)])]}
        

    def __init__(self, llm):
        self.llm = llm
        self.system_prompt = SystemMessage("Você é um assistente útil. Responda as perguntas com clareza e objetividade.")
        graph_builder = StateGraph(self.State)

        # Adding Nodes
        graph_builder.add_node("chatbot", self.chatbot)

        # Connecting Nodes

        graph_builder.add_edge(START, "chatbot") # specifying entrypoint
        graph_builder.add_edge("chatbot", END)

        # Making Memory
        memory = MemorySaver() # saves a state according to an id in memory
        # can be updated to use a database instead. Not our focus for now.

        # Compiling
        self.graph = graph_builder.compile(checkpointer=memory) # we can now use the graph (run the state machine)

    # Seeing made graph
    def print_graph(self):
        print(self.graph.get_graph().draw_ascii())

    def set_system_prompt(self, system_prompt):
        self.system_prompt = system_prompt

    def invoke(self, prompt, chat_id, original_prompt=None):

        if original_prompt is None:
            original_prompt = prompt

        config = {
            "configurable": {
                "thread_id": chat_id
            }
        }
        return self.graph.invoke(input={"original_prompt": original_prompt, "final_prompt": prompt}, config=config)

    def get_chat_history(self, chat_id):
        config = {
            "configurable": {
                "thread_id": chat_id
            }
        }
        return self.graph.get_state(config).values['messages']