import urllib
import urllib2
import json
import traceback


class WeChat(object):

    OAUTH_URL = "https://open.weixin.qq.com/connect/oauth2/authorize?"
    ACCESS_TOKEN_URL = "https://api.weixin.qq.com/sns/oauth2/access_token?"
    REFRESH_TOKEN_URL = "https://api.weixin.qq.com/sns/oauth2/refresh_token?"
    GET_USER_INFO_URL = "https://api.weixin.qq.com/sns/userinfo?"

    def __init__(self, app_id, app_secret):
        self.app_id = app_id
        self.app_secret = app_secret

    def get_oauth2_url(self, redirect_url, scope='snsapi_base', response_type='code', state='1'):
        """
        :param redirect_url: url for wechat callback
        :param scope: 'snsapi_base' or 'snsapi_base'
        :param response_type: 'code'
        :param state: '1'
        :return: url to oauth
        """
        params = {"appid": self.app_id,
                  "response_type": response_type,
                  "redirect_uri": redirect_url,
                  "scope": scope,
                  "state": state}
        url = "%s%s#wechat_redirect" % (self.OAUTH_URL, urllib.urlencode(params))
        return url

    def get_web_access_token_by_code(self, code, grant_type="authorization_code"):
        """
        :param code: code came from the redirect of oauth2
        :param grant_type: 'authorization_code'
        :return:
        {
            "access_token":"ACCESS_TOKEN",
            "expires_in":7200,
            "refresh_token":"REFRESH_TOKEN",
            "openid":"OPENID",
            "scope":"SCOPE"
        }
        """
        try:
            params = {"appid": self.app_id,
                      "secret": self.app_secret,
                      "code": code,
                      "grant_type": grant_type}
            url = "%s%s" % (self.ACCESS_TOKEN_URL, urllib.urlencode(params))
            res = urllib2.urlopen(url)
            data = res.read()
            return json.loads(data)
        except:
            print traceback.format_exc()
            return {}

    def refresh_token(self, refresh_token):
        """
        :param refresh_token: str
        :return:
        {
            "access_token":"ACCESS_TOKEN",
            "expires_in":7200,
            "refresh_token":"REFRESH_TOKEN",
            "openid":"OPENID",
            "scope":"SCOPE"
        }
        """
        try:
            params = {"appid": self.app_id,
                      "secret": self.app_secret,
                      "grant_type": refresh_token}
            url = "%s%s" % (self.REFRESH_TOKEN_URL, urllib.urlencode(params))
            res = urllib2.urlopen(url)
            data = res.read()
            return json.loads(data)
        except:
            print traceback.format_exc()
            return {}

    def get_wc_user_info(self, open_id, access_token, lang='zh_CN'):
        """
        :param open_id: wechat open_id
        :param access_token: wechat access_token
        :param lang: 'zh_CN'
        :return:
        {
            "openid":" OPENID",
            "nickname": NICKNAME,
            "sex":"1",
            "province":"PROVINCE"
            "city":"CITY",
            "country":"COUNTRY",
            "headimgurl": "http://wx.qlogo.cn/mmopen/g3MonUZtNHkdmzicIlibx6iaFqA",
            "privilege":[
                "PRIVILEGE1"
                "PRIVILEGE2"
            ],
            "unionid": "o6_bmasdasdsad6_2sgVt7hMZOPfL"
        }
        """
        try:
            params = {"access_token": access_token,
                      "openid": open_id,
                      "lang": lang}
            url = "%s%s" % (self.GET_USER_INFO_URL, urllib.urlencode(params))
            res = urllib2.urlopen(url)
            data = res.read()
            return json.loads(data)
        except:
            print traceback.format_exc()
            return {}
