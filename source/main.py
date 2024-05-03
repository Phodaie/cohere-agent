import os
import asyncio
from termcolor import colored
import cohere


API_KEY = os.environ.get("COHERE_API_KEY") # fill in your environment variable name here
co = cohere.Client(API_KEY)


tools = [

    {
        "name": "llm_worker",
        "description": "Powerful Large Language Model specialized in generating educational course content.",
        "parameter_definitions": {
            "task": {
                "description": "The task to be completed by the Large Language Model.",
                "type": "str",
                "required": True
            }
        }
    }
]

async def llm_worker(task: str , ids = []) -> str:
    """
    Function to utilizes Large Language Model to complete the task
    """
    await asyncio.sleep(4)

    preable = "Only for the larger request, if possible breakdown the request into smaller sub-tasks and assign them to other LLMS. Assemlbe the results and provide the final output."
    
    print(colored(f"Task {ids}:","green") ,"\n", f"{task}")
    if len(ids) < 2:
    
        response = co.chat(
            preamble=preable,
            message=task,
            tools=tools,
            model="command-r-plus"
        )
    else:
        response = co.chat( 
            message=task,
            model="command-r-plus"
        )

    tool_results = await call_tools_parallel(response=response , ids=ids)
    response = co.chat(
        message=task,
        tools=tools,
        tool_results=tool_results,
        preamble=preable,
        model="command-r-plus",
        
    )
    
    print(colored(f"Response {ids}:", 'red'), "\n", f"{response.text}")
    return response.text
    

functions_map = {
    "llm_worker": llm_worker,
    
}




async def call_tools_parallel(response , ids=[]):

    tasks = []

    if not response.tool_calls:
        return []
    
    for index , tool_call in enumerate(response.tool_calls):
        
        #print(tool_call.name , tool_call.parameters)
        if tool_call.name in functions_map:
            func = functions_map[tool_call.name]
            
            child_ids = ids + [index + 1]
            task = asyncio.create_task(func(**tool_call.parameters , ids=child_ids))
            tasks.append(task)

    
    outputs = await asyncio.gather(*tasks)

    tool_results = []
    for tool_call , output in zip(response.tool_calls , outputs):
        tool_results.append({
            "call": tool_call,
            "outputs": [{"result" : output}]
        })
        
    return tool_results






async def main():
    preamble = """
    ## Task & Context
    You an instruction designer who create complete courses. You first design the syllabus, then create the course content, and finally, you design the assessments. 
    To speed up the process, you assign sub-tasks to other LLMS.

    ## Style Guide
    The course content you generate should be in a formal and professional style. Use complete sentences and avoid contractions.
    """


    message = "Create an introductory course on Python programming. Include the following topics: variables, data types, loops, and functions."

    response = co.chat(
        message=message,
        tools=tools,
        preamble=preamble,
        model="command-r-plus"
    )

    tool_results = await call_tools_parallel(response=response)


    response = co.chat(
        message=message,
        tools=tools,
        tool_results=tool_results,
        preamble=preamble,
        model="command-r-plus",
        
    )

    print("Final answer:")
    print(response.text)

if __name__ == "__main__":
    asyncio.run(main())