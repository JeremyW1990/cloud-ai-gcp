from google.auth.exceptions import DefaultCredentialsError
import google.cloud.logging
import logging

client = google.cloud.logging.Client()
client.setup_logging()


def create_agent_util(client, agent_data, strategy):
    try:
        
        vendor_agent = strategy.init_assistant(client, agent_data.get('name'), agent_data.get('instructions'))
        
        # Log the vendor_agent dictionary
        logging.info(f"Vendor agent details: {vendor_agent}")
        
        vendor_agent_id = vendor_agent.get('id') 
        logging.info(f"Vendor agent ID: {vendor_agent_id}")
        return vendor_agent_id, None
    except Exception as e:
        logging.error(f"An error occurred while creating agent: {str(e)}")
        return None, str(e)