import openai
import os
from dotenv import load_dotenv
import jsonschema
from RetrieveJournal import create_page_in_notion
from WhisperCapture import test_whisper_transcription

# Load environment variables
load_dotenv("Journal.env")

# Instantiate the OpenAI client object
client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

# Define the function signature for structured output
function = {
    "name": "create_notion_page_data",
    "description": "Extract structured data for Notion from the transcription text.",
    "parameters": {
        "type": "object",
        "properties": {
            "name": {"type": "string", "description": "The name of the transaction."},
            "status": {"type": "string", "description": "The status of the transaction."},
            "amount": {"type": "number", "description": "The transaction amount."},
            "action": {"type": "string", "description": "The action performed (e.g., Deposit, Transfer)."},
            "note": {"type": "string", "description": "Any additional notes."},
            "date": {"type": "string", "description": "Transaction date in YYYY-MM-DD format."},
            "fromAcct": {"type": "string", "description": "ID of the originating account."},
            "toAcct": {"type": "string", "description": "ID of the destination account."}
        },
        "required": ["name", "amount", "action", "date", "fromAcct", "toAcct"]
    }
}

# Example transcription for testing
example_transcription = """
    "I made a deposit of $150 on October 15th, 2024 from my main account to my savings account. The status is completed, and the note is 'Monthly deposit'."
"""

# Function to request structured output from OpenAI
def get_structured_output_from_ai(transcription):
    try:
        response = client.chat.completions.create(
            model="gpt-4o-2024-08-06",  # GPT-4 with function calling
            messages=[
                {
                    "role": "system",
                    "content": "You are an AI that extracts structured data from transaction-related speech input. From Account and To Account values must be one of the following: Freedom, Chase Checking, Fuel Expense, Chase Savings, Amazon"
                },
                {
                    "role": "user",
                    "content": transcription
                }
            ],
            functions=[function],
            function_call="auto",
        )
        print( response.json() )
        # Extract the structured response
        structured_data = response.choices[0].message['function_call']['arguments']
        print("Structured Data:", structured_data)
        return structured_data

    except Exception as e:
        print(f"Error extracting structured data: {e}")
        return None

# Main function to control workflow
# Test VS Code
def main():
    # Step 1: Capture transcription from Whisper API
    transcription = test_whisper_transcription()

    # Step 2: Send the transcription to OpenAI for structured output
    parsed_data = get_structured_output_from_ai(transcription)

    # Step 3: Validate the response and create a new page in Notion
    if parsed_data:
        try:
            # Define the schema to validate the parsed data
            schema = {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "status": {"type": "string"},
                    "amount": {"type": "number"},
                    "action": {"type": "string"},
                    "note": {"type": "string"},
                    "date": {"type": "string", "format": "date"},
                    "fromAcct": {"type": "string"},
                    "toAcct": {"type": "string"}
                },
                "required": ["name", "amount", "action", "date", "fromAcct", "toAcct"]
            }

            # Validate the parsed data against the schema
            jsonschema.validate(instance=parsed_data, schema=schema)

            # Step 4: Create a new page in Notion using the parsed data
            create_page_in_notion(
                name=parsed_data['name'],
                status=parsed_data['status'],
                amount=parsed_data['amount'],
                action=parsed_data['action'],
                note=parsed_data['note'],
                date=parsed_data['date'],
                fromAcct=parsed_data['fromAcct'],
                toAcct=parsed_data['toAcct']
            )

        except jsonschema.ValidationError as e:
            print(f"Validation error: {e}")
    else:
        print("Failed to get structured output from AI")

# Test function to simulate transcription and get structured output
def test_structured_output():
    transcription = "I used my Freedom card yesterday to buy $75.00 of Diesel Fuel."
    get_structured_output_from_ai(transcription)

if __name__ == "__main__":
    #main()  # Uncomment this for production use
    test_structured_output()  # Uncomment this for testing
