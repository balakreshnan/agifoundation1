from collections import defaultdict
import datetime
from pathlib import Path
import tempfile
import time
from typing import Sequence
import PyPDF2
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.conditions import MaxMessageTermination, TextMentionTermination
from autogen_agentchat.messages import AgentEvent, ChatMessage
from autogen_agentchat.teams import SelectorGroupChat
from autogen_agentchat.ui import Console
from autogen_ext.models.openai import AzureOpenAIChatCompletionClient
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.teams import MagenticOneGroupChat
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_core.code_executor import CodeBlock
from autogen_core import CancellationToken
from autogen_ext.code_executors.local import LocalCommandLineCodeExecutor
from autogen_agentchat.ui import Console
import asyncio
import os
import venv
from bs4 import BeautifulSoup
from openai import AzureOpenAI
from dotenv import load_dotenv
import streamlit as st
from PIL import Image
import base64
import requests
import io

# Load .env file
load_dotenv()

client = AzureOpenAI(
  azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT_VISION"), 
  api_key=os.getenv("AZURE_OPENAI_KEY_VISION"),  
  api_version="2024-10-21"
)

model_name = "gpt-4o-2"

model_client = AzureOpenAIChatCompletionClient(model="gpt-4o", 
                                               azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"), 
                                               api_key=os.getenv("AZURE_OPENAI_API_KEY"), 
                                               api_version="2024-10-21")

async def agent_process(query):
    returntext = ""

    planning_agent = AssistantAgent(
        "PlanningAgent",
        description="An agent for planning tasks, this agent should be the first to engage when given a new task.",
        model_client=model_client,
        system_message="""
        You are a planning agent.
        Your job is to break down complex tasks into smaller, manageable subtasks.
        Your team members are:
            CreateCodeAgent: Create code for the given task.
            Testplanagent: Create test plan for the given task.
            Createunittestagent: Create unit test for the given task. Create Code.
            Executeunittestagent: Execute unit test for the given task. Execute Code.
            Validateunittestagent: Collect all results from unit test and validate the results.
            Finalizeunittestagent: Finalize the unit test and provide the results.
            
        You only plan and delegate tasks - you do not execute them yourself.
        Also only use web search agent for non manufacturing complaince data.

        When assigning tasks, use this format:
        1. <agent> : <task>

        After all tasks are complete, summarize the findings and end with "TERMINATE".
        Extract Title content from the document. Show the Title, url as citations which is provided as url: as [url1] [url2].
        """,
    )

    create_Code_agent = AssistantAgent(
        "CreateCodeAgent",
        description="Create code for the given task.",
        #tools=[bing_search_and_summarize],
        model_client=model_client,
        system_message="""
        Create code for the given task. Create code in python
        """,
    )

    test_plan_agent = AssistantAgent(
        "Testplanagent",
        description="Create test plan for the given task.",
        #tools=[bing_search_and_summarize],
        model_client=model_client,
        system_message="""
        You are an expert software testing engineer specializing in unit test design. Your task is to create a comprehensive unit test plan for the following piece of code. Analyze the code thoroughly and provide a detailed testing strategy. Your response should include:
        Code Analysis:
        Briefly describe the purpose and functionality of the provided code.
        Identify the main components, functions, or methods that need to be tested.
        Highlight any potential edge cases or complex logic that require special attention.
        Test Objectives:
        List the primary objectives of the unit tests for this code.
        Specify what aspects of the code's functionality need to be verified.
        Test Cases:
        Provide a detailed list of test cases, including:
        a. Test case ID
        b. Description of the test case
        c. Input values or preconditions
        d. Expected output or postconditions
        e. Any specific setup required for the test
        Edge Cases and Boundary Testing:
        Identify and list specific edge cases that should be tested.
        Describe boundary value tests that should be performed.
        Error Handling and Exception Testing:
        Outline tests for error conditions and exception handling.
        Specify how to test the code's behavior with invalid inputs or unexpected scenarios.
        Mocking and Dependency Handling:
        If the code has external dependencies, describe how these should be mocked or stubbed for isolated testing.
        Performance Considerations:
        If applicable, suggest performance-related tests (e.g., stress testing, load testing).
        Code Coverage:
        Recommend a target code coverage percentage for the unit tests.
        Identify any parts of the code that might be challenging to cover and suggest strategies.
        Testing Framework and Tools:
        Recommend appropriate testing frameworks or tools for implementing these unit tests.
        Additional Considerations:
        Mention any specific coding standards or best practices that should be followed in writing the tests.
        Suggest any refactoring that might make the code more testable, if applicable.
        Please provide this unit test plan in a clear, structured format. Your plan should be thorough enough to guide a developer in implementing a comprehensive set of unit tests for the given code.
        """,
    )

    create_unit_test_agent = AssistantAgent(
        "Createunittestagent",
        description="Create unit test for the given task. Create Code.",
        #tools=[bing_search_and_summarize],
        model_client=model_client,
        system_message="""
        You are an expert software developer specializing in unit testing. Based on the comprehensive unit test plan provided, your task is to generate the actual unit test code for the given piece of software. Use the following guidelines to create the test code:
        Code Analysis:
        Review the original code and the test plan's analysis.
        Ensure you understand the code's functionality and components to be tested.
        Testing Framework:
        Use the recommended testing framework from the test plan. If not specified, choose an appropriate framework for the language (e.g., JUnit for Java, pytest for Python).
        Test Structure:
        Create a test class or module that corresponds to the main class or module being tested.
        Implement individual test methods for each test case identified in the plan.
        Test Implementation:
        For each test case in the plan:
        Write a test method with a clear, descriptive name.
        Implement the test logic according to the test case description.
        Use appropriate assertions to verify expected outcomes.
        Include comments explaining the purpose of each test.
        Setup and Teardown:
        Implement setup and teardown methods if required for test initialization or cleanup.
        Mocking and Stubbing:
        Use mocking frameworks as needed to isolate the code under test from its dependencies.
        Implement mock objects or stubs as described in the test plan.
        Edge Cases and Boundary Testing:
        Implement specific tests for the edge cases and boundary conditions identified in the plan.
        Error Handling and Exceptions:
        Write tests to verify proper error handling and exception throwing as outlined in the plan.
        Performance Tests:
        If applicable, implement any performance-related tests suggested in the plan.
        Code Coverage:
        Ensure your tests aim to achieve the recommended code coverage percentage.
        Pay special attention to covering complex or hard-to-reach parts of the code.
        Best Practices:
        Follow coding standards and best practices for unit testing in the chosen language.
        Ensure tests are independent and can run in any order.
        Keep tests focused, testing one thing at a time.
        Documentation:
        Include a brief comment at the beginning of the test file explaining its purpose and any setup required to run the tests.
        Please provide the complete, executable test code based on these instructions. The code should be well-structured, properly formatted, and ready for immediate use in a development environment. Include any necessary import statements or additional setup code required for the tests to run successfully.
        """,
    )

    execute_unit_test_agent = AssistantAgent(
        "Executeunittestagent",
        description="Execute unit test for the given task. execute Code created by Create unit test agent.",
        #tools=[bing_search_and_summarize],
        model_client=model_client,
        system_message="""
        You are an advanced unit test execution agent. Your task is to run all unit tests in the project and collect the results. Follow these instructions:
        Scan the project directory for all test files.
        Execute each test file using the appropriate testing framework.
        Collect test results in JUnit XML format.
        Store all test result XML files in the /output folder.
        Generate a summary report of all test executions.
        Specific steps:
        Identify the testing framework used in the project (e.g., pytest, JUnit, MSTest).
        Use the framework's CLI command to run tests with XML output. For example:
        For pytest: pytest --junitxml=/output/test_results.xml
        For JUnit: java -cp <classpath> org.junit.runner.JUnitCore <test_class> -xmloutput /output/test_results.xml
        If multiple test files exist, run each separately and generate individual XML results.
        After all tests are executed, create a summary report in the /output folder, including:
        Total number of tests run
        Number of passed tests
        Number of failed tests
        Overall pass rate
        Execution time for each test suite
        If any test failures occur, provide detailed information in the summary report, including:
        Name of the failed test
        Error message
        Stack trace (if available)
        Ensure all generated files are stored in the /output folder.
        Execute these steps and report any issues encountered during the process. The final output should be a collection of XML test result files and a summary report, all located in the /output folder.
        """,
    )

    validate_unit_test_agent = AssistantAgent(
        "Validateunittestagent",
        description="Validate unit test for the given task. Collect output from Execute unit test agent and validate if good.",
        #tools=[bing_search_and_summarize],
        model_client=model_client,
        system_message="""
        You are an expert software quality assurance analyst specializing in unit test validation. Your task is to review and validate the unit test results for a given project. Use the output collected from the Execute Unit Test agent stored in the /output folder. Follow these steps to analyze and provide feedback on the test results:
        Review Test Execution Summary:
        Examine the summary report in the /output folder.
        Note the total number of tests, pass/fail counts, and overall pass rate.
        Analyze Individual Test Results:
        Review each XML result file in the /output folder.
        Pay attention to failed tests, error messages, and stack traces.
        Evaluate Test Coverage:
        If available, review code coverage reports.
        Determine if the coverage meets the project's target percentage.
        Assess Test Quality:
        Evaluate if the tests adequately cover all critical functionality.
        Check for proper assertion usage and test independence.
        Identify Patterns in Failures:
        Look for common themes or recurring issues in failed tests.
        Validate Against Requirements:
        Ensure the tests align with the project's requirements and specifications.
        Performance Evaluation:
        Review execution times for individual tests and the entire suite.
        Flag any unusually slow tests.
        Provide Detailed Feedback:
        Summarize your findings, including:
            a. Overall assessment of test quality and effectiveness
            b. Specific issues or concerns identified
            c. Areas of strength in the test suite
            d. Recommendations for improvement
        Suggest Changes:
            If necessary, propose specific changes such as:
            a. Additional test cases to improve coverage
            b. Modifications to existing tests for better effectiveness
            c. Refactoring suggestions to improve test maintainability
            d. Performance optimization recommendations
        Action Items:
        Create a list of prioritized action items for the development team.
        Your output should be a comprehensive report that includes:
        An executive summary of the test results
        Detailed analysis of test coverage, quality, and performance
        Specific feedback on strengths and weaknesses
        Prioritized list of suggested improvements or changes
        Any critical issues that require immediate attention
        Ensure your feedback is constructive, clear, and actionable. If the test results are satisfactory, provide positive reinforcement along with any minor suggestions for further enhancement.
        """,
    )

    finalize_unit_test_agent = AssistantAgent(
        "Finalizeunittestagent",
        description="Finalize unit test for the results and summarize output as charts.",
        #tools=[bing_search_and_summarize],
        model_client=model_client,
        system_message="""
        You are a data visualization expert specializing in software testing metrics. Your task is to finalize the unit test results and create a visually appealing summary using charts. Use the validated test results and feedback from the previous steps. Follow these instructions to create a comprehensive visual report:
        Data Collection:
        Gather all relevant data from the /output folder, including test execution summaries and individual test results.
        Compile key metrics such as total tests, pass/fail counts, code coverage percentages, and execution times.
        Chart Creation:
        Create the following charts to visualize the test results:
        a. Test Execution Summary Pie Chart:
        Show the proportion of passed, failed, and skipped tests.
        b. Code Coverage Bar Chart:
        Display code coverage percentages for different modules or components.
        Include a line indicating the target coverage percentage.
        c. Test Execution Time Histogram:
        Plot the distribution of test execution times.
        Highlight any outliers or unusually slow tests.
        d. Test Results Trend Line Chart:
        If historical data is available, show the trend of pass/fail rates over time.
        e. Test Category Breakdown Stacked Bar Chart:
        Categorize tests (e.g., unit, integration, UI) and show their respective pass/fail rates.
        f. Top 5 Failing Tests Bar Chart:
        Identify and display the most frequently failing tests.
        Summary Dashboard:
        Create a single-page dashboard that includes all the above charts.
        Add a brief text summary highlighting key findings and metrics.
        Interactive Elements (if applicable):
        If the output format allows, make charts interactive with hover-over details and click-through capabilities.
        Color Scheme and Accessibility:
        Use a consistent, visually appealing color scheme across all charts.
        Ensure the charts are readable for color-blind individuals.
        Annotations:
        Add clear titles, labels, and legends to each chart.
        Include brief annotations to highlight significant findings or explain anomalies.
        Export Options:
        Provide the dashboard in multiple formats (e.g., PNG, PDF, interactive HTML).
        Recommendations Section:
        Based on the visualized data, include a section with data-driven recommendations for improving test quality and coverage.
        Executive Summary:
        Create a brief textual summary (1-2 paragraphs) interpreting the charts and highlighting the most important findings.
        Your final output should be a visually compelling, easy-to-understand set of charts that effectively communicate the unit test results. The charts should be accompanied by a brief explanatory text and actionable recommendations. Ensure that the visual summary accurately reflects the test results and provides valuable insights for both technical and non-technical stakeholders.
        """,
    )


    text_mention_termination = TextMentionTermination("TERMINATE")
    max_messages_termination = MaxMessageTermination(max_messages=25)
    termination = text_mention_termination | max_messages_termination

    # model_client_mini = AzureOpenAIChatCompletionClient(model="gpt-4o", 
    #                                             azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"), 
    #                                             api_key=os.getenv("AZURE_OPENAI_API_KEY"), 
    #                                             api_version="2024-10-21")


    # team = RoundRobinGroupChat([planning_agent, create_Code_agent, test_plan_agent, create_unit_test_agent,
    #                               execute_unit_test_agent, validate_unit_test_agent, finalize_unit_test_agent], 
    #                             # model_client=model_client,
    #                             termination_condition=termination, max_turns=1)
    team = MagenticOneGroupChat([planning_agent, create_Code_agent, test_plan_agent, create_unit_test_agent,
                                 execute_unit_test_agent, validate_unit_test_agent, finalize_unit_test_agent], 
                                 model_client=model_client,
                                 termination_condition=termination, max_turns=1)

    result = await Console(team.run_stream(task=query))
    #print(result)  # Process the result or output here
    # Extract and print only the message content
    returntxt = ""
    returntxtall = ""
    for message in result.messages:
        # print('inside loop - ' , message.content)
        returntxt = str(message.content)
        returntxtall += str(message.content) + "\n"

    # work_dir = Path("coding")
    # work_dir.mkdir(exist_ok=True)

    # venv_dir =  "/.venv"
    # venv_builder = venv.EnvBuilder(with_pip=True)
    # venv_builder.create(venv_dir)
    # venv_context = venv_builder.ensure_directories(venv_dir)

    # local_executor = LocalCommandLineCodeExecutor(work_dir=work_dir, virtual_env_context=venv_context)
    # await local_executor.execute_code_blocks(
    #     code_blocks=[
    #         CodeBlock(language="bash", code="pip install matplotlib"),
    #     ],
    #     cancellation_token=CancellationToken(),
    # )


    return returntext, returntxtall

def main():
    st.title("Unit Test Assistant Chat")
    if prompt := st.chat_input("Write a code to display Tesla Stock for past 4 years?", key="chat1"):
        # Call the extractproductinfo function
        #st.write("Searching for the query: ", prompt)
        st.chat_message("user").markdown(prompt, unsafe_allow_html=True)
        #st.session_state.chat_history.append({"role": "user", "message": prompt})
        starttime = datetime.datetime.now()
        result = asyncio.run(agent_process(prompt))
        rfttopics, agenthistory = result
            
        endtime = datetime.datetime.now()
        #st.markdown(f"Time taken to process: {endtime - starttime}", unsafe_allow_html=True)
        rfttopics += f"\n Time taken to process: {endtime - starttime}"
        #st.session_state.chat_history.append({"role": "assistant", "message": rfttopics})
        st.chat_message("assistant").markdown(agenthistory, unsafe_allow_html=True)

if __name__ == "__main__":
    main()