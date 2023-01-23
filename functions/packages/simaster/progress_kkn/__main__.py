from http import HTTPStatus

from Simaster import Simaster

def main(args):
    username = args.get("username")
    password = args.get("password")

    if not username:
        return {
            "statusCode": HTTPStatus.BAD_REQUEST,
            "body": "Username is required"
        }

    if not password:
        return {
            "statusCode": HTTPStatus.BAD_REQUEST,
            "body": "Password is required"
        }
    
    simaster = Simaster(credential={
        "username": username,
        "password": password
    })

    if not simaster.login():
        return {
            "statusCode": HTTPStatus.UNAUTHORIZED,
            "body": "Cannot login, username or password not match"
        }

    data_proker = simaster.data_proker()

    for i in range(0, len(data_proker)):
        data_proker[i]['detail'] = simaster.detail_proker(data_proker[i]['url'])
    
    return {
        "statusCode": HTTPStatus.OK,
        "body": {
            "pokok": data_proker,
            "bantu": simaster.detail_proker(data_proker[0]['url'], is_bantu=True)
        }
    }