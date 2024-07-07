import requests
import random
import time

# constants
URL_ME = "https://gateway.blum.codes/v1/user/me"
URL_BALANCE = "https://game-domain.blum.codes/api/v1/user/balance"
URL_PLAY_GAME = "https://game-domain.blum.codes/api/v1/game/play"
URL_CLAIM_REWARD = "https://game-domain.blum.codes/api/v1/game/claim"


class InvalidToken(Exception):
    ...


class BlumAPI:
    def __init__(self, authorization_token) -> None:
        self.headers = {
            'Authorization': authorization_token
        }

    def request(self, request_method, url, payload=None):
        response = getattr(requests, request_method)(url, headers=self.headers, data=payload)
        if response.status_code in [401]:
            raise InvalidToken(response.text)
        return response

    def get_me(self):
        response = self.request('get', URL_ME)
        if not response.ok:
            raise Exception(f'Проблема при получении имени пользователя!\nТекст ошибки с сервера: {response.text}')
        return response.json()

    def get_balance(self):
        response = self.request('get', URL_BALANCE)
        if not response.ok:
            raise Exception('Проблема при получении баланса!\nТекст ошибки с сервера: {response.text}')
        return response.json()

    def play_game(self):
        response = self.request('post', URL_PLAY_GAME)
        if not response.ok:
            raise Exception(f'При попытке сыграть в игру произошла ошибка!\nТекст ошибки с сервера: {response.text}')
        return response.json()

    def claim_reward(self, game_id: str, points: int):
        payload = {
            'gameId': game_id,
            'points': points
        }

        response = self.request('post', URL_CLAIM_REWARD, payload=payload)
        if not response.ok:
            raise Exception(f'При попытке собрать награду произошла ошибка!\nТекст ошибки с сервера: {response.text}')


def main():
    autorization_token = input('Введи токен авторизации Blum: ')

    try:
        while True:
            blum_api = BlumAPI(authorization_token=autorization_token)
            username = blum_api.get_me().get('username')

            while True:
                print(
                    f'\nПривет {username}! Что вы хотите сделать?\n1. Я хочу получить поинты за игры\n2. Прошлая сессия крашнулась, я хочу получить поинты за игру которая началась.')
                choice = input('Сделайте свой выбор (1 - 2): ')

                if choice == '1':
                    balance_data = blum_api.get_balance()
                    avilable_balance = balance_data.get('availableBalance')
                    game_passes = balance_data.get('playPasses')

                    print(
                        f'\nБаланс вашего аккаунта: {avilable_balance}\nКол-во доступных игр на вашем аккаунте: {game_passes}')

                    while True:
                        games_count = int(input(f'\nВыберите кол-во игр которое хотите сыграть: '))
                        if isinstance(games_count, int):
                            if 0 < games_count <= game_passes:
                                break

                        print('Введите допустимое число!')
                        continue

                    for game_number in range(1, games_count + 1):
                        print(f'\n[+] Игра номер {game_number} была взята в обработку!')
                        response = blum_api.play_game()

                        game_id = response.get('gameId')
                        points = random.randrange(260, 280)

                        print(f'[+] Игра номер {game_number} была успешно начата!\nИдентификатор вашей игры: {game_id}')
                        print(f'[+] Ждем 35 секунд до завершения игры...')
                        time.sleep(35)
                        blum_api.claim_reward(game_id, points)
                        print(
                            f'[+] Игра номер {game_number} была успешно отработана!\n\nВы получили: {points}\nБаланс: {sum(map(float, [avilable_balance, points]))}')
                        time.sleep(1)

                    print('\n[+] Все игры были успешно отработаны!')
                    input('Нажмите ENTER для продолжения...')

                elif choice == '2':
                    game_id = input('Введите идентификатор вашей игры: ')
                    points = random.randrange(260, 280)
                    blum_api.claim_reward(game_id, points)
                    print(f'\n[+] Успех! Вы получили {points}!\nНомер игры: {game_id}')
                    input('Нажмите ENTER для продолжения...')

                else:
                    print('\nНеверный ввод!\nПожалуйста, выберите 1 или 2!')
                    time.sleep(1.5)

    except InvalidToken as e:
        print(
            f'\nОшибка с токеном, возможные причины:\n1. Токен устарел, введите новый токен!\n2. Возможно ошибка на стороне сервера, повторите попытку чуть позже!\n\nТекст ошибки полученный с сервера: {e}')

    except Exception as e:
        print(f'\nERROR! {e}')


if __name__ == '__main__':
    main()