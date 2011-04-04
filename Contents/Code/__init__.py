#s4u.se
import os
import urllib2, urllib, string, random, types, unicodedata, re, datetime

SRC_URL = 'http://api.s4u.se/Beta/DemoKey/xml/%s/%s/%s/%s'
PLEX_USERAGENT = 'plexapp.com v9.x'
subtitleExt       = ['utf','utf8','utf-8','sub','srt','smi','rt','ssa','aqt','jss','ass','idx']
 
def Start():
#  HTTP.CacheTime = CACHE_1DAY
  HTTP.CacheTime = 0
  HTTP.Headers['User-agent'] = PLEX_USERAGENT

class S4uAgentMovies(Agent.Movies):
  name = 'S4u.se'
  languages = [Locale.Language.English]
  primary_provider = False
  contributes_to = ['com.plexapp.agents.imdb']
  
  def GetFixedXML(self, url, isHtml=False):		# function for getting XML in the corresponding URL
    xml = HTTP.Request(url)
#    Log("xml in GetFixedXML = %s" % xml)
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
					dir = path.split('/')[-1]
					url = SRC_URL %('movie', 'fname', urllib.quote(dir), '')	# URL for movie name search
					Log('Looking for match for File %s and size %d at %s' % (dir, p.size, url))
					xml = self.GetFixedXML(url) # to get XML for search result
					subtitleResponse = xml #XML.ElementFromURL(SRC_URL + basename)
				if subtitleResponse.xpath("/xmlresult/movie"):
					Log('Yes %s matches for movie!' % subtitleResponse.xpath("//info/hits_movie")[0].text)
					if not subtitleResponse.xpath("//sub/download_file"):
						Log('No, no subs available for the movie %s ;(' % (subtitleResponse.xpath("//movie/title")[0].text))
						continue
					Log('Yes %s subs for the movie %s will try to download the first match.' % (subtitleResponse.xpath("//info/hits_movie_sub")[0].text, subtitleResponse.xpath("//movie/title")[0].text))
					subUrl = subtitleResponse.xpath('//sub/download_file')[0].text
					subType = subtitleResponse.xpath('//sub/file_type')[0].text
					fileName = path + "/" + basename + ".sv." + subType
					subData = ""
					Log('Trying to download %s of type %s and save it as %s'  % (subUrl, subType, fileName))
					if os.path.isfile(fileName): #Test if file exists.
						Log('The file %s already exist, no need to download.' % fileName)
						try:
							fd = os.open(fileName,os.O_RDONLY)
							subData = os.read(fd,os.stat(fileName).st_size)
							os.close(fd)
						except Exception, e:
							Log('An error occurred reading %s file! \n%s' % (fileName,e))
					else:
						try:
							fd = os.open(fileName, os.O_RDWR|os.O_TRUNC|os.O_CREAT)
							#os.close(fd)
							#fd = os.open(fileName, os.O_RDWR|os.O_APPEND)
							subFile = HTTP.Request(subUrl)
							subData = subFile + " thx erlis." #Let's skip unzipping at this time..
							os.write(fd,subData) #Save file.					
							os.close(fd)
						except Exception, e:
							Log('An r occurred saving %s file! \n%s' % (fileName,e)) #Load the sub from url rather than file.
							p.subtitles[Locale.Language.Match('sv')][subUrl] = Proxy.Media(subData, ext=subType)
					p.subtitles[Locale.Language.Match('sv')][basename + ".sv." + subType] = Proxy.LocalFile(fileName)
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
  
  def GetFixedXML(self, url, isHtml=False):		# function for getting XML in the corresponding URL
    xml = HTTP.Request(url)
    #Log("xml in GetFixedXML = %s" % xml)
    return XML.ElementFromString(xml, isHtml)


  def search(self, results, media, lang):
    results.Append(MetadataSearchResult(
      id    = 'null',
      score = 100  ))

  def update(self, metadata, media, lang):
    HTTP.Headers['User-agent'] = 'plexapp.com v9.0'
#    proxy = XMLRPC.Proxy(OS_API)
    for s in media.seasons:
      # just like in the Local Media Agent, if we have a date-based season skip for now.
      if int(s) < 1900:
        for e in media.seasons[s].episodes:
          for i in media.seasons[s].episodes[e].items:
            for p in i.parts:
							filename = p.file.decode('utf-8')
							path = os.path.dirname(filename)
				#		if 'video_ts' == path.lower().split('/')[-1]:
				#			path= '/'.join(path.split('/')[:-1])
							basename = os.path.basename(filename)
							basename = os.path.splitext(basename)[0] #Remove filetype
							url = SRC_URL % ('serie', 'fname', urllib.quote(basename), '')	# URL for movie name search
							Log('Looking for match for file %s at %s' % (basename, url))
							xml = self.GetFixedXML(url) # to get XML for search result
							subtitleResponse = xml #XML.ElementFromURL(SRC_URL + basename)
							if not subtitleResponse.xpath("/xmlresult/serie"): #No match for filename, perhaps we can match the dir name.
								dir = path.split('/')[-1]
								url = SRC_URL %('serie', 'fname', urllib.quote(dir), '')	# URL for movie name search
								Log('Looking for match for dirname %s and size %d at %s' % (dir, p.size, url))
								xml = self.GetFixedXML(url) # to get XML for search result
								subtitleResponse = xml #XML.ElementFromURL(SRC_URL + basename)
							if subtitleResponse.xpath("/xmlresult/serie"):
								Log('Yes %s matches for serie!' % subtitleResponse.xpath("//info/hits_serie")[0].text)
								if not subtitleResponse.xpath("//sub/download_file"):
									Log('No, no subs available for the serie %s ;(' % (subtitleResponse.xpath("//serie/title")[0].text))
									return
								Log('Yes %s subs for the serie %s will try to download the first match.' % (subtitleResponse.xpath("//info/hits_serie_sub")[0].text, subtitleResponse.xpath("//serie/title")[0].text))
								subUrl = subtitleResponse.xpath('//sub/download_file')[0].text
								subType = subtitleResponse.xpath('//sub/file_type')[0].text
								fileName = path + "/" + basename + ".sv." + subType
								subData = ""
								Log('Trying to download %s of type %s and save it as %s'  % (subUrl, subType, fileName))
								if os.path.isfile(fileName): #Test if file exists.
									Log('The file %s already exist, no need to download.' % fileName)
									try:
										fd = os.open(fileName,os.O_RDONLY)
										subData = os.read(fd,os.stat(fileName).st_size)
										os.close(fd)
									except Exception, e:
										Log('An error occurred reading %s file! \n%s' % (fileName,e))
								else:
									try:
										fd = os.open(fileName, os.O_RDWR|os.O_TRUNC|os.O_CREAT)
										#os.close(fd)
										#fd = os.open(fileName, os.O_RDWR|os.O_APPEND)
										subFile = HTTP.Request(subUrl)
										subData = subFile + " " #Let's skip unzipping at this time..
										os.write(fd,subData) #Save file.					
										os.close(fd)
									except Exception, e:
										Log('An r occurred saving %s file! \n%s' % (fileName,e)) #Load the sub from url rather than file.
										p.subtitles[Locale.Language.Match('sv')][subUrl] = Proxy.Media(subData, ext=subType)
								p.subtitles[Locale.Language.Match('sv')][basename + ".sv." + subType] = Proxy.LocalFile(fileName)
							else:
								Log('No subtitles available for language sv and serie %s S%02dE%02d' % (media.title, int(s), int(e)))
