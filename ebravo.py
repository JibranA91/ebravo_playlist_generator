import pandas as pd
import urllib.request
import re
import time

all_tv_channels_link = 'http://ebravo.pk/classic/webtv'

ebravo_dict = {}
weburl = urllib.request.urlopen(all_tv_channels_link)
channel_names = str(weburl.read())

all_links = re.findall("webtv-[0-9][0-9][0-9].html", channel_names)
all_links += re.findall("webtv-[0-9][0-9].html", channel_names)


all_link_indexes = [channel_names.find(x) for x in all_links]
all_link_names = []
for i in all_link_indexes:
    t_start, t_end = 'title="', '">'
    title_sindex = channel_names.find(t_start, i)
    title_eindex = channel_names.find(t_end, title_sindex)
    all_link_names.append(channel_names[title_sindex+len(t_start):title_eindex])

channel_logos = []
for i in all_link_indexes:
    t_start, t_end = '<img src="', '" '
    title_sindex = channel_names.find(t_start, i)
    title_eindex = channel_names.find(t_end, title_sindex)
    logo = 'http://ebravo.pk/classic/'+channel_names[title_sindex+len(t_start):title_eindex]
    channel_logos.append(logo)


ebravo_dict['channel_name'] = all_link_names
ebravo_dict['channel_link'] = [all_tv_channels_link+str(link).replace('webtv','') for link in all_links]
ebravo_dict['channel_logos'] = channel_logos
ebravo_channels = pd.DataFrame(ebravo_dict)
ebravo_channels['m3u8_link'] = ''
ebravo_channels = ebravo_channels.sort_values('channel_name').reset_index(drop=True)
ebravo_channels.to_csv('ebravo_channels.csv', index=False)

m3u8_links = []
for i in range(len(ebravo_channels)):
    if ebravo_channels.loc[i].m3u8_link != '':
        print(f'link for {ebravo_channels.loc[i].channel_name} already present')
        continue
    tv_channel_link = ebravo_channels.loc[i].channel_link
    weburl = urllib.request.urlopen(tv_channel_link)
    channel_page = str(weburl.read())

    m3u8_link = re.findall(r"video id.*.m3u8", channel_page)[0]
    m3u8_link = m3u8_link[len(m3u8_link)-m3u8_link[::-1].find(':ptth')-5:]

    ebravo_channels.loc[i,'m3u8_link'] = m3u8_link
    ebravo_channels.to_csv('ebravo_channels.csv', index=False)
    print(f"{i+1}/{len(ebravo_channels)} {all_link_names[i]} {m3u8_link}")
    time.sleep(10)

# m3u8 format
"""
#EXTINF:11 group-title="eBravo" tvg-logo="http://ebravo.pk/classic/uploads/webtv//8907d9b8bf77411163d9a513010de12f.jpg", ARY  Zindagi
http://58.65.194.14:1935/live/ARY-Zindagi.stream/playlist.m3u8
"""
with open('stormfiber.m3u', 'w') as f:
    for i in range(len(ebravo_channels)):
        if i == 0: _=f.write('#EXTM3U\n')
        ch_desc = f'''#EXTINF:{i+1} group-title="eBravo" tvg-logo="{ebravo_channels.loc[i,'channel_logos']}", {ebravo_channels.loc[i,'channel_name']}'''
        _=f.write(ch_desc+'\n')
        _=f.write(ebravo_channels.loc[i,"m3u8_link"]+'\n')
