import json
import requests
import os.path
from tinydb import TinyDB, Query, operations


AUTH_KEYS = {}

with open('types.json') as types_file:    
    types = json.load(types_file)
songsdb = TinyDB('songs.json')

def set_keys(app_id, api_key):
    global AUTH_KEYS
    AUTH_KEYS = {
            'app_id': app_id,
            'api_key': api_key
            }


class BaseParseClass(object):
        # _connection_error_message = ('Cannot connect to muzis.ru')
    # _parse_special_classes = ['users', 'login', 'roles', 'files', 'events',
            # 'push', 'installations', 'functions', 'jobs',
            # 'requestPasswordReset', 'events', 'products',
            # 'roles']


    def __init__(self):
        #, app_id=None, api_key=None):
        self._url = 'http://muzis.ru'
        self._furl = 'http://f.muzis.ru'

        # if self._parse_class_name is None:
            # self._parse_class_name = self.__class__.__name__.lower()

        # collection = (self._parse_class_name if
                      # self._parse_class_name in
                      # self._parse_special_classes else
                      # 'classes/' + self._parse_class_name)

        # self._base_url = self._url + collection

        # app_id = app_id if app_id else AUTH_KEYS.get('app_id')
        # api_key = api_key if api_key else AUTH_KEYS.get('api_key')

        # self._headers = {
            # "X-Parse-Application-Id": app_id,
            # "X-Parse-REST-API-Key": api_key,
            # "Content-Type": "application/json"}
 # q_track=None, q_performer=None, q_lirics=None, q_value=None, size=None, offset=None, sort=None
    def search(self, track=None, performer=None, lyrics=None, value=None, size=None, offset=None, sort=None):
        params={}
        def addParams(value,name,params):
            if value is not None:
                params[name]=value
        addParams(track,"q_track",params)
        addParams(performer,"q_performer",params)
        addParams(lyrics,"q_lyrics",params)
        addParams(value,"q_value",params)
        addParams(size,"size",params)
        addParams(offset,"offset",params)
        addParams(sort,"sort",params)
        r=requests.post(self._url+"/api/search.api", params)
        result = r.json()
        songs = result["songs"]
        for s in songs:
            self.addSong(s)
        performers = result["performers"]
        # print(performers)
        # print(songs)

    def stream_from_values(self, values=None, size=None, operator=None):
        params={}
        def addParams(value,name,params):
            if value is not None:
                params[name]=value
        addParams(values,"values",params)
        addParams(size,"size",params)
        addParams(operator,"operator",params)
        r=requests.post(self._url+"/api/stream_from_values.api", params)
        result = r.json()
        print(result)
        songs = result["songs"]
        for s in songs:
            self.addSong(s)
        return songs

    def similar_performers(self, performer_id=None, size=None):
        params={}
        def addParams(value,name,params):
            if value is not None:
                params[name]=value
        addParams(performer_id,"performer_id",params)
        addParams(size,"size",params)
        r=requests.post(self._url+"/api/similar_performers.api", params)
        print(r.text)
        # result = r.json()
        # performers = result["performers"]
        # print(result)
    # def json(self):
        # payload = {k: v for k, v in self.__dict__.iteritems()
                   # if not k.startswith('_')}

        # return payload
    def addSong(self,song):
        if not songsdb.search(Query()["id"] == song["id"]):
            songsdb.insert(song)
            print("song added")
        else:
            print("song exist")

    def get(self,filename):
        local_filename = "files/"+filename 
        if not os.path.isfile(local_filename):
            print(local_filename+' downloaded')
            r = requests.get(self._furl+"/"+filename, stream=True)
            with open(local_filename, 'wb') as f:
                for chunk in r.iter_content(chunk_size=1024): 
                    if chunk: # filter out keep-alive new chunks
                        f.write(chunk)
        else:
            print(local_filename+' already downloaded')
        return local_filename


    # def get(self, **kwargs):
        # objectId = kwargs.pop('objectId', None)
        # createdBy = kwargs.pop('createdBy', None)
        # parentCategory = kwargs.pop('parentCategory', None)
        # status = kwargs.pop('status', None)
        # school = kwargs.pop('school', None)
        # type = kwargs.pop('type', None)
        # emailVerified = kwargs.pop('emailVerified', None)
        # params = kwargs

        # url = ("{base}/{id}".format(base=self._base_url, id=objectId) if
               # objectId else self._base_url)

        # where = {}
        # if createdBy:
            # where["createdBy"] = {"__type": "Pointer", "className": "_User",
                                  # "objectId": createdBy}

        # if school:
            # where["school"] = {"__type": "Pointer", "className": "School",
                               # "objectId": school}

        # if parentCategory:
            # where["parentCategory"] = {
                # "__type": "Pointer",
                # "className": "TaskCategory",
                # "objectId": parentCategory}

        # if status:
            # where["status"] = status

        # if type:
            # where["type"] = type

        # if emailVerified:
            # where["emailVerified"] = True

        # if where:
            # params['where'] = json.dumps(where)

        # try:
            # payload = requests.get(url, headers=self._headers, params=params)
            # data = 

            # return payload.json()

        # except Exception as e:
            # return {'error': e.message}

    # def save(self):
        # data = self.json()

        # createdBy = data.pop('createdBy', False)
        # if createdBy:
            # data['createdBy'] = {"__type": "Pointer", "className": "_User",
                                 # "objectId": createdBy}

        # if data.get('objectId', False):
            # return self.put(data=data)

        # try:
            # return self.post(data=data)
        # except Exception as e:
            # return {'error': e.message}

    # def post(self, data):
        # try:
            # payload = requests.post(self._base_url, data=json.dumps(data),
                                    # headers=self._headers)
            # return payload.json()
        # except Exception as e:
            # return {'error': e.message}

    # def put(self, data):
        # url = (self._base_url + "/" + data.get('objectId')
               # if data.get('objectId') else self._base_url)

        # try:
            # payload = requests.put(url=url,
                                   # data=json.dumps(data),
                                   # headers=self._headers)

            # return payload.json()
        # except Exception as e:
            # return {'error': e.message}

    # def delete(self, objectId):
        # url = self._base_url + "/" + objectId

        # try:
            # res = requests.delete(url=url, headers=self._headers)

            # return res.json()
        # except Exception as e:
            # return {'error': e.message}

