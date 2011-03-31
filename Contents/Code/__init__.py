#s4u.se
import os, string, hashlib
import urllib2, urllib, string, random, types, unicodedata, re, datetime

SRC_URL = 'http://api.s4u.se/Beta/DemoKey/xml/%s/%s/%s/%s'
#DL_URL = 'http://www.undertexter.se/laddatext.php?id='
#OS_LANGUAGE_CODES = 'http://www.opensubtitles.org/addons/export_languages.php'
PLEX_USERAGENT = 'plexapp.com v9.x'
subtitleExt       = ['utf','utf8','utf-8','sub','srt','smi','rt','ssa','aqt','jss','ass','idx']
 
def Start():
#  HTTP.CacheTime = CACHE_1DAY
  HTTP.CacheTime = 0
  HTTP.Headers['User-agent'] = PLEX_USERAGENT

#@expose
#def GetImdbIdFromHash(openSubtitlesHash, lang):
#  proxy = XMLRPC.Proxy(OS_API)
#  try:
#    os_movieInfo = proxy.CheckMovieHash('',[openSubtitlesHash])
#  except:
#    return None
#    
#  if os_movieInfo['data'][openSubtitlesHash] != []:
#    return MetadataSearchResult(
#      id    = "tt" + str(os_movieInfo['data'][openSubtitlesHash]['MovieImdbID']),
#      name  = str(os_movieInfo['data'][openSubtitlesHash]['MovieName']),
#      year  = int(os_movieInfo['data'][openSubtitlesHash]['MovieYear']),
#      lang  = lang,
#      score = 90)
#  else:
#    return None
#  
class S4uAgentMovies(Agent.Movies):
  name = 'S4u.se'
  languages = [Locale.Language.English]
  primary_provider = False
  contributes_to = ['com.plexapp.agents.imdb']
  
  def GetFixedXML(self, url, isHtml=False):		# function for getting XML in the corresponding URL
    xml = HTTP.Request(url)
    # Log("xml in GetFixedXML = %s" % xml)
    return XML.ElementFromString(xml, isHtml)

 
  def search(self, results, media, lang):
    results.Append(MetadataSearchResult(
      id    = 'null',
      score = 100  ))
    
  def update(self, metadata, media, lang):
#    HTTP.Headers['User-agent'] = PLEX_USERAGENT
#    proxy = XMLRPC.Proxy(OS_API)
    for i in media.items:
      for p in i.parts:
				filename = p.file.decode('utf-8')
				path = os.path.dirname(filename)
		#		if 'video_ts' == path.lower().split('/')[-1]:
		#			path= '/'.join(path.split('/')[:-1])
				basename = os.path.basename(filename)
				basename = os.path.splitext(basename)[0] #Remove filetype
				url = SRC_URL % ('movie', 'fname', urllib.quote(basename), '')	# URL for movie name search
				Log('Looking for match for File %s at %s' % (basename, url))
				xml = self.GetFixedXML(url) # to get XML for search result
				subtitleResponse = xml #XML.ElementFromURL(SRC_URL + basename)
				if not subtitleResponse.xpath("/xmlresult/movie"): #No match for filename, perhaps we can match the dir name.
					dir = '/'.join(path.split('/')[:-1])
					url = SRC_URL %('movie', 'fname', urllib.quote(dir))	# URL for movie name search
					Log('Looking for match for File %s and size %d at %s' % (dir, p.size, url))
					xml = self.GetFixedXML(url) # to get XML for search result
					subtitleResponse = xml #XML.ElementFromURL(SRC_URL + basename)
				if subtitleResponse.xpath("/xmlresult/movie"):
					Log('Yes %s matches for movie!' % subtitleResponse.xpath("//info/hits_movie")[0].text)
					if not subtitleResponse.xpath("//sub/download_file"):
						Log('No, no subs available for the movie %s ;(' % (subtitleResponse.xpath("//movie/title")[0].text))
						return
					Log('Yes %s subs for the movie %s will try to download the first match.' % (subtitleResponse.xpath("//info/hits_movie_sub")[0].text, subtitleResponse.xpath("//movie/title")[0].text))
					subUrl = subtitleResponse.xpath('//sub/download_file')[0].text
					subType = subtitleResponse.xpath('//sub/file_type')[0].text
					Log('Trying to download %s of type %s'  % (subUrl, subType))
					subFile = HTTP.Request(subUrl)
					subData = subFile #Let's skip unzipping at this time..
					p.subtitles[Locale.Language.Match('sv')][subUrl] = Proxy.Media(subData, ext=subType)
				else:
					Log('No subtitles available for language sv')

			#     for st in subtitleResponse: #remove any subtitle formats we don't recognize
			#       if st['SubFormat'] not in subtitleExt:
			#         Log('Removing a subtitle of type: ' + st['SubFormat'])
			#         subtitleResponse.remove(st)
			#     st = sorted(subtitleResponse, key=lambda k: int(k['SubDownloadsCnt']), reverse=True)[0] #most downloaded subtitle file for current language
			#     if st['SubFormat'] in subtitleExt:
			#       subUrl = st['SubDownloadLink']
			#  subGz = HTTP.Request(subUrl, headers={'Accept-Encoding':''}).content
			# subData = Archive.GzipDecompress(subGz)
				

class S4uAgentTV(Agent.TV_Shows):
  name = 'S4u.se'
  languages = [Locale.Language.English]
  primary_provider = False
  contributes_to = ['com.plexapp.agents.thetvdb']

  def search(self, results, media, lang):
    results.Append(MetadataSearchResult(
      id    = 'null',
      score = 100  ))

  def update(self, metadata, media, lang):
    HTTP.Headers['User-agent'] = 'plexapp.com v9.0'
    proxy = XMLRPC.Proxy(OS_API)
    for s in media.seasons:
      # just like in the Local Media Agent, if we have a date-based season skip for now.
      if int(s) < 1900:
        for e in media.seasons[s].episodes:
          for i in media.seasons[s].episodes[e].items:
            for p in i.parts:
              token = proxy.LogIn('', '', 'en', OS_PLEX_USERAGENT)['token']
              langList = [Prefs["langPref1"]]
              if Prefs["langPref2"] != 'None':
                langList.append(Prefs["langPref2"])
              for l in langList:
                Log('Looking for match for GUID %s and size %d' % (p.openSubtitleHash, p.size))
                subtitleResponse = proxy.SearchSubtitles(token,[{'sublanguageid':l, 'moviehash':p.openSubtitleHash, 'moviebytesize':str(p.size)}])['data']
                if subtitleResponse != False:
                  for st in subtitleResponse: #remove any subtitle formats we don't recognize
                    if st['SubFormat'] not in subtitleExt:
                      Log('Removing a subtitle of type: ' + st['SubFormat'])
                      subtitleResponse.remove(st)
                  st = sorted(subtitleResponse, key=lambda k: int(k['SubDownloadsCnt']), reverse=True)[0] #most downloaded subtitle file for current language
                  if st['SubFormat'] in subtitleExt:
                    subUrl = st['SubDownloadLink']
                    subGz = HTTP.Request(subUrl, headers={'Accept-Encoding':''}).content
                    subData = Archive.GzipDecompress(subGz)
                    p.subtitles[Locale.Language.Match(st['SubLanguageID'])][subUrl] = Proxy.Media(subData, ext=st['SubFormat'])
                else:
                  Log('No subtitles available for language ' + l)
