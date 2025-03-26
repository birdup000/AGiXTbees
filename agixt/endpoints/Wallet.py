from fastapi import APIRouter, Depends, HTTPException
from Models import WalletResponseModel
from Agent import Agent
from MagicalAuth import get_user_id
import logging

app = APIRouter()

@app.get(
    "/api/agent/{agent_name}/wallet",
    tags=["Agent"],
    response_model=WalletResponseModel,
    dependencies=[Depends(get_user_id)],
)
async def get_wallet_details(agent_name: str, user=Depends(get_user_id)):
    """
    Retrieves the private key and passphrase for the agent's Solana wallet.
    Strictly enforces one wallet per agent, created on first access via get_agent_config.
    """
    try:
        agent = Agent(agent_name=agent_name, user=user)
        agent_config = agent.get_agent_config() # This ensures wallet exists or is created
        settings = agent_config.get("settings", {})

        private_key = settings.get("SOLANA_WALLET_API_KEY")
        passphrase = settings.get("SOLANA_WALLET_PASSPHRASE_API_KEY")
        address = settings.get("SOLANA_WALLET_ADDRESS") # Verify address exists too

        if not private_key or not passphrase or not address:
            logging.error(f"Wallet details incomplete or missing for agent {agent_name} after get_agent_config.")
            raise HTTPException(
                status_code=404,
                detail=f"Wallet details not found for agent '{agent_name}'. Wallet should be created automatically.",
            )

        return WalletResponseModel(private_key=private_key, passphrase=passphrase)

    except HTTPException as e:
        # Re-raise HTTPException to return specific error codes
        raise e
    except Exception as e:
        logging.error(f"Error retrieving wallet details for agent {agent_name}: {e}")
        raise HTTPException(
            status_code=500, detail=f"Internal server error retrieving wallet details: {e}"
        )