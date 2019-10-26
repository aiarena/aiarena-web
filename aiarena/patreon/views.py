from constance import config
from django.shortcuts import redirect
from django.views import View

from aiarena.patreon.models import PatreonAccountBind
from aiarena.patreon.patreon import PatreonOAuth, PatreonApi


class PatreonBindView(View):
    def get(self, request):
        return redirect("https://www.patreon.com/oauth2/authorize"
                        "?response_type=code"
                        "&client_id=" + config.PATREON_CLIENT_ID +
                        "&redirect_uri=https%3A%2F%2F127.0.0.1%3A8000%2Fpatreon%2Foauth%2Fredirect")


class PatreonCallbackView(View):
    def get(self, request):
        oauth_client = PatreonOAuth(config.PATREON_CLIENT_ID, config.PATREON_CLIENT_SECRET)
        tokens = oauth_client.get_tokens(request.GET['code'], 'https://127.0.0.1:8000/patreon/oauth/redirect')

        account_bind, created = PatreonAccountBind.objects.get_or_create(user=request.user)
        account_bind.access_token = tokens['access_token']
        account_bind.refresh_token = tokens['refresh_token']
        account_bind.save()

        api_client = PatreonApi(account_bind.access_token)

        user = api_client.current_user()
        patreon_level = 'none'
        for entry in user['included']:
            if entry['type'] == 'pledge':
                if entry['attributes']['amount_cents'] >= 10000:  # diamond
                    patreon_level = 'diamond'
                    break
                elif entry['attributes']['amount_cents'] >= 5000:  # platinum
                    patreon_level = 'platinum'
                    break
                elif entry['attributes']['amount_cents'] >= 2500:  # gold
                    patreon_level = 'gold'
                    break
                elif entry['attributes']['amount_cents'] >= 1000:  # silver
                    patreon_level = 'silver'
                    break
                elif entry['attributes']['amount_cents'] >= 500:  # bronze
                    patreon_level = 'bronze'
                    break
                else:
                    raise Exception("Unexpected Patreon tier encountered!")

        request.user.patreon_level = patreon_level
        request.user.save()
        return redirect('profile')
