import json
import quart
import quart_cors
from quart import request
from stellar_sdk.transaction_envelope import TransactionEnvelope
from stellar_sdk.keypair import Keypair
import configparser

app = quart_cors.cors(quart.Quart(__name__), allow_origin="*")

@app.post("/sign")
async def sign():
    try:
        headers = quart.request.headers
        bearer = headers.get('Authorization')    # Bearer token
        if bearer is None or bearer.split()[1] != "987654321":
            raise Exception("Unauthenticated")

        request = await quart.request.get_json(force=True)
        if "transaction" not in request:
            raise Exception("missing transaction parameter")
        if "network_passphrase" not in request:
            raise Exception("missing network_passphrase parameter")
        
        xdr = request["transaction"]
        network_passphrase = request["network_passphrase"]
        transaction = TransactionEnvelope.from_xdr(xdr, network_passphrase= network_passphrase)
        config = configparser.ConfigParser()
        config.read('signing.ini')
        secret = config['signing']['secret']
        kp = Keypair.from_secret(secret)
        transaction.sign(kp)
        
        res = {}
        res['transaction'] = transaction.to_xdr()
        res['network_passphrase'] = network_passphrase
    
        return quart.Response(response=json.dumps(res), status=200)
    except Exception as e:
        return quart.Response(response=str(e), status=400)

def main():
    app.run(debug=True, host="0.0.0.0", port=5003)
    
if __name__ == "__main__":
    main()