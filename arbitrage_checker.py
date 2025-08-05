import requests, asyncio
from aiogram import Bot

bot = Bot(token="TON_TELEGRAM_TOKEN_ICI")
chat_id = "TON_CHAT_ID_ICI"

# Pools à vérifier sur Arbitrum
DEXS = {
    "UniswapV3": "https://api.thegraph.com/subgraphs/name/ianlapham/arbitrum-minimal",
    "SushiSwap": "https://api.thegraph.com/subgraphs/name/sushiswap/arbitrum-exchange",
    "Camelot": "https://api.thegraph.com/subgraphs/name/camelotlabs/camelot-amm",
}

TOKENS = {
    "USDC": "0xff970a61a04b1ca14834a43f5de4533ebdbb5cc8",
    "WETH": "0x82af49447d8a07e3bd95bd0d56f35241523fbab1"
}

async def send_alert(msg):
    await bot.send_message(chat_id, msg, parse_mode="Markdown")

def get_price(pool_api, tokenA, tokenB):
    query = """
    {
      pairs(where:{
        token0_in:["%s","%s"],
        token1_in:["%s","%s"]
      }) {
        token0 { symbol }
        token1 { symbol }
        token0Price
        token1Price
      }
    }
    """ % (tokenA.lower(), tokenB.lower(), tokenA.lower(), tokenB.lower())
    resp = requests.post(pool_api, json={'query': query})
    if resp.status_code != 200:
        return None
    data = resp.json()
    pairs = data.get('data', {}).get('pairs', [])
    for pair in pairs:
        symbols = (pair["token0"]["symbol"], pair["token1"]["symbol"])
        if "USDC" in symbols and "WETH" in symbols:
            return float(pair["token0Price"])
    return None

async def check_all_dexs():
    prices = {}
    for dex, api_url in DEXS.items():
        price = get_price(api_url, TOKENS["USDC"], TOKENS["WETH"])
        if price:
            prices[dex] = price
            print(f"{dex} USDC/WETH: {price:.6f}")

    # Vérification arbitrage (écart supérieur à 0.3%)
    for dex1, price1 in prices.items():
        for dex2, price2 in prices.items():
            if dex1 != dex2:
                diff = abs(price1 - price2) / price2
                if diff >= 0.003:  # >0.3% arbitrage
                    msg = f"🚨 Arbitrage détecté:\n\n{dex1}: {price1:.6f}\n{dex2}: {price2:.6f}\nDifférence: {diff:.2%}"
                    await send_alert(msg)
                    return  # envoie une seule alerte à la fois

async def main_loop():
    while True:
        try:
            await check_all_dexs()
        except Exception as e:
            print("Erreur:", e)
        await asyncio.sleep(30)  # Vérifie toutes les 30 secondes

if __name__ == "__main__":
    asyncio.run(main_loop())

