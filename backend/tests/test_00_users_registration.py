import pytest

from users.models import User


class Test00UsersRegistration:
    url_signup = '/api/users/'
    url_token = '/api/auth/token/login/'
    url_admin_create_user = '/api/users/'

    @pytest.mark.django_db(transaction=True)
    def test_00_nodata_signup(self, client):
        request_type = 'POST'
        response = client.post(self.url_signup)

        assert response.status_code != 404, (
            f'Страница `{self.url_signup}` не найдена, проверьте этот адрес в *urls.py*'
        )
        code = 400
        assert response.status_code == code, (
            f'Проверьте, что при {request_type} запросе `{self.url_signup}` без параметров '
            f'не создается пользователь и возвращается статус {code}'
        )
        response_json = response.json()
        empty_fields = ['email', 'username', 'first_name', 'last_name', 'password']
        for field in empty_fields:
            assert (field in response_json.keys()
                    and isinstance(response_json[field], list)), (
                f'Проверьте, что при {request_type} запросе `{self.url_signup}` без параметров '
                f'в ответе есть сообщение о том, какие поля заполенены неправильно'
            )

    @pytest.mark.django_db(transaction=True)
    def test_00_invalid_data_signup(self, client):
        invalid_email = 'invalid_email'
        invalid_username = 'invalid_username@yamdb.fake'

        invalid_data = {
            'email': invalid_email,
            'username': invalid_username
        }
        request_type = 'POST'
        response = client.post(self.url_signup, data=invalid_data)

        assert response.status_code != 404, (
            f'Страница `{self.url_signup}` не найдена, проверьте этот адрес в *urls.py*'
        )
        code = 400
        assert response.status_code == code, (
            f'Проверьте, что при {request_type} запросе `{self.url_signup}` с невалидными данными '
            f'не создается пользователь и возвращается статус {code}'
        )

        response_json = response.json()
        invalid_fields = ['email']
        for field in invalid_fields:
            assert (field in response_json.keys()
                    and isinstance(response_json[field], list)), (
                f'Проверьте, что при {request_type} запросе `{self.url_signup}` с невалидными параметрами, '
                f'в ответе есть сообщение о том, какие поля заполенены неправильно'
            )

        valid_email = 'validemail@yamdb.fake'
        invalid_data = {
            'email': valid_email,
        }
        response = client.post(self.url_signup, data=invalid_data)
        assert response.status_code == code, (
            f'Проверьте, что при {request_type} запросе `{self.url_signup}` без username '
            f'нельзя создать пользователя и возвращается статус {code}'
        )

    @pytest.mark.django_db(transaction=True)
    def test_00_valid_data_user_signup(self, client):

        valid_email = 'valid@yamdb.fake'
        valid_username = 'valid_username'
        valid_first_name = 'first'
        valid_last_name = 'last'
        valid_password = 'pass123kkk...'

        valid_data = {
            'email': valid_email,
            'username': valid_username,
            'first_name': valid_first_name,
            'last_name': valid_last_name,
            'password': valid_password
        }
        request_type = 'POST'
        response = client.post(self.url_signup, data=valid_data)

        assert response.status_code != 404, (
            f'Страница `{self.url_signup}` не найдена, проверьте этот адрес в *urls.py*'
        )

        code = 201
        assert response.status_code == code, (
            f'Проверьте, что при {request_type} запросе `{self.url_signup}` с валидными данными '
            f'создается пользователь и возвращается статус {code}'
        )

        new_user = User.objects.filter(email=valid_email)
        assert new_user.exists(), (
            f'Проверьте, что при {request_type} запросе `{self.url_signup}` с валидными данными '
            f'создается пользователь и возвращается статус {code}'
        )

        # Test confirmation code
        response_data = response.json()
        response_data.pop('id')
        valid_data.pop('password')
        assert response_data == valid_data, (
            f'Проверьте, что при {request_type} запросе `{self.url_signup}` с валидными данными '
            f'создается пользователь и возвращается статус {code}'
        )

        new_user.delete()
    #
    # @pytest.mark.django_db(transaction=True)
    # def test_00_valid_data_admin_create_user(self, admin_client):
    #
    #     valid_email = 'valid@yamdb.fake'
    #     valid_username = 'valid_username'
    #     outbox_before_count = len(mail.outbox)
    #
    #     valid_data = {
    #         'email': valid_email,
    #         'username': valid_username
    #     }
    #     request_type = 'POST'
    #     response = admin_client.post(self.url_admin_create_user, data=valid_data)
    #     outbox_after = mail.outbox
    #
    #     assert response.status_code != 404, (
    #         f'Страница `{self.url_admin_create_user}` не найдена, проверьте этот адрес в *urls.py*'
    #     )
    #
    #     code = 201
    #     assert response.status_code == code, (
    #         f'Проверьте, что при {request_type} запросе `{self.url_admin_create_user}` с валидными данными '
    #         f'от имени администратора, создается пользователь и возвращается статус {code}'
    #     )
    #     response_json = response.json()
    #     for field in valid_data:
    #         assert field in response_json and valid_data.get(field) == response_json.get(field), (
    #             f'Проверьте, что при {request_type} запросе `{self.url_admin_create_user}` с валидными данными '
    #             f'от имени администратора, в ответ приходит созданный объект пользователя в виде словаря'
    #         )
    #
    #     new_user = User.objects.filter(email=valid_email)
    #     assert new_user.exists(), (
    #         f'Проверьте, что при {request_type} запросе `{self.url_admin_create_user}` с валидными данными '
    #         f'от имени администратора, в БД создается пользователь и возвращается статус {code}'
    #     )
    #
    #     # Test confirmation code not sent to user after admin registers him
    #     assert len(outbox_after) == outbox_before_count, (
    #         f'Проверьте, что при {request_type} запросе `{self.url_admin_create_user}` с валидными данными '
    #         f'от имени администратора, пользователю НЕ приходит email с кодом подтверждения'
    #     )
    #
    #     new_user.delete()

    @pytest.mark.django_db(transaction=True)
    def test_00_login_invalid_data(self, admin_client, client):

        request_type = 'POST'
        response = client.post(self.url_token)
        assert response.status_code != 404, (
            f'Страница `{self.url_token}` не найдена, проверьте этот адрес в *urls.py*'
        )

        code = 400
        assert response.status_code == code, (
            f'Проверьте, что при POST запросе `{self.url_token}` без параметров, '
            f'возвращается статус {code}'
        )

        invalid_data = {
            'password': '1234567'
        }
        response = client.post(self.url_token, data=invalid_data)
        assert response.status_code == code, (
            f'Проверьте, что при POST запросе `{self.url_token}` без email, '
            f'возвращается статус {code}'
        )

        invalid_data = {
            'email': 'dd@ddd',
            'confirmation_code': 12345
        }
        response = client.post(self.url_token, data=invalid_data)
        code = 400
        assert response.status_code == code, (
            f'Проверьте, что при POST запросе `{self.url_token}` с несуществующим email, '
            f'возвращается статус {code}'
        )

        valid_email = 'testadmin@yamdb.fake'
        valid_password = '1234567'

        valid_data = {
            'email': valid_email,
            'password': valid_password
        }
        response = client.post(self.url_token, data=valid_data)
        code = 200
        assert response.status_code == code, (
            f'Проверьте, что при {request_type} запросе `{self.url_token}` с валидными данными '
            f'создается пользователь и возвращается статус {code} {response}'
        )

        invalid_data = {
            'email': valid_email,
            'password': '11111111'
        }
        response = client.post(self.url_token, data=invalid_data)
        code = 400
        assert response.status_code == code, (
            f'Проверьте, что при POST запросе `{self.url_token}` с валидным username, '
            f'но невалидным confirmation_code, возвращается статус {code}'
        )

    @pytest.mark.django_db(transaction=True)
    def test_00_registration_same_email_restricted(self, client):
        valid_email_1 = 'test_duplicate_1@yamdb.fake'
        valid_email_2 = 'test_duplicate_2@yamdb.fake'
        valid_username_1 = 'valid_username_1'
        valid_username_2 = 'valid_username_2'
        valid_first_name = 'first'
        valid_last_name = 'last'
        valid_password = 'pass11..2233'
        request_type = 'POST'

        valid_data = {
            'email': valid_email_1,
            'username': valid_username_1,
            'first_name': valid_first_name,
            'last_name': valid_last_name,
            'password': valid_password
        }
        response = client.post(self.url_signup, data=valid_data)
        code = 201
        assert response.status_code == code, (
            f'Проверьте, что при {request_type} запросе `{self.url_signup}` '
            f'можно создать пользователя с валидными данными и возвращается статус {code}'
        )

        duplicate_email_data = {
            'email': valid_email_1,
            'username': valid_username_1,
            'first_name': valid_first_name,
            'last_name': valid_last_name,
            'password': valid_password
        }
        response = client.post(self.url_signup, data=duplicate_email_data)
        code = 400
        assert response.status_code == code, (
            f'Проверьте, что при {request_type} запросе `{self.url_signup}` нельзя создать '
            f'пользователя, email которого уже зарегистрирован и возвращается статус {code}'
        )

