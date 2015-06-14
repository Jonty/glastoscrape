#!/usr/bin/python
import unicodecsv

artists = []
with open('glastonbury_2015_schedule_filtered.csv', 'r') as fp:
    f = unicodecsv.reader(fp, delimiter=',', encoding='utf-8')
    for row in f:
        if row[0] == 'title':
            continue

        artists.append('["%s","%s"]' % (row[0], row[5]))

js = '''
var listNode = document.getElementById("artistList");
while (listNode.firstChild) {
    listNode.removeChild(listNode.firstChild);
}
var Artists = [%s]
Artists.map(function(artist) {
    var li = document.createElement('li');
    li.innerHTML = artist[0] + '<input type="hidden" value="' + artist[1] + '" name="artists[]"><img src="http://cdn.last.fm/depth/buttons/bin_simple.gif" alt="Remove this artist" title="Remove this artist">';
    listNode.appendChild(li)
})
$('uploadSubmit').click()
''' % ','.join(artists)

with open('lfm_js_console_paste.js', 'w') as f:
    f.write(js.encode('utf8'))
