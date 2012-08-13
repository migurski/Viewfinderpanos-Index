from math import floor
from itertools import count
from sys import stderr, stdout
from zipfile import ZipFile, BadZipfile
from csv import writer

from time import time
from urlparse import urlparse, urljoin
from httplib import HTTPConnection
from os.path import basename
from cStringIO import StringIO
from datetime import timedelta
from os import SEEK_SET, SEEK_CUR, SEEK_END

class RemoteFileObject:
    """ Implement enough of this to be useful:
        http://docs.python.org/release/2.5.2/lib/bltin-file-objects.html
        
        Pull data from a remote URL with HTTP range headers.
    """

    def __init__(self, url, verbose=False, block_size=(16 * 1024)):
        self.verbose = verbose

        # scheme://host/path;parameters?query#fragment
        (scheme, host, path, parameters, query, fragment) = urlparse(url)
        
        self.host = host
        self.rest = path + (query and ('?' + query) or '')

        self.offset = 0
        self.length = self.get_length()
        self.chunks = {}
        
        self.block_size = block_size
        self.start_time = time()

    def get_length(self):
        """
        """
        conn = HTTPConnection(self.host)
        conn.request('GET', self.rest, headers={'Range': '0-1'})
        length = int(conn.getresponse().getheader('content-length'))
        
        if self.verbose:
            print >> stderr, length, 'bytes in', basename(self.rest)

        return length

    def get_range(self, start, end):
        """
        """
        headers = {'Range': 'bytes=%(start)d-%(end)d' % locals()}

        conn = HTTPConnection(self.host)
        conn.request('GET', self.rest, headers=headers)
        return conn.getresponse().read()

    def read(self, count=None):
        """ Read /count/ bytes from the resource at the current offset.
        """
        if count is None:
            # to the end
            count = self.length - self.offset

        out = StringIO()

        while count:
            chunk_offset = self.block_size * (self.offset / self.block_size)
            
            if chunk_offset not in self.chunks:
                range = chunk_offset, min(self.length, self.offset + self.block_size) - 1
                self.chunks[chunk_offset] = StringIO(self.get_range(*range))
                
                if self.verbose:
                    loaded = float(self.block_size) * len(self.chunks) / self.length
                    expect = (time() - self.start_time) / loaded
                    remain = max(0, int(expect * (1 - loaded)))
                    print >> stderr, '%.1f%%' % min(100, 100 * loaded),
                    print >> stderr, 'of', basename(self.rest),
                    print >> stderr, 'with', timedelta(seconds=remain), 'to go'

            chunk = self.chunks[chunk_offset]
            in_chunk_offset = self.offset % self.block_size
            in_chunk_count = min(count, self.block_size - in_chunk_offset)
            
            chunk.seek(in_chunk_offset, SEEK_SET)
            out.write(chunk.read(in_chunk_count))
            
            count -= in_chunk_count
            self.offset += in_chunk_count

        out.seek(0)
        return out.read()

    def seek(self, offset, whence=SEEK_SET):
        """ Seek to the specified offset.
            /whence/ behaves as with other file-like objects:
                http://docs.python.org/lib/bltin-file-objects.html
        """
        if whence == SEEK_SET:
            self.offset = offset
        elif whence == SEEK_CUR:
            self.offset += offset
        elif whence == SEEK_END:
            self.offset = self.length + offset

    def tell(self):
        return self.offset

def filenames():
    '''
    '''
    letters = 'abcdefghijklmnopqrstuvwxyz'
    
    for (prefix, factor) in [('', 1), ('s', -1)]:
        for (lat, letter) in zip(range(2, 87, 4), letters):
            lat = int(4.0 * floor(factor * lat / 4.0))
            
            for (lon, number) in zip(range(-180, 180, 6), count(1)):
                for suffix in ('', 'v2'):
                    yield lat, lon, '%(prefix)s%(letter)s%(number)02d%(suffix)s' % locals()

zip_urls = '''
http://www.viewfinderpanoramas.org/dem3/A32.zip
http://www.viewfinderpanoramas.org/dem3/A33.zip
http://www.viewfinderpanoramas.org/dem3/A34.zip
http://www.viewfinderpanoramas.org/dem3/A35.zip
http://www.viewfinderpanoramas.org/dem3/A36.zip
http://www.viewfinderpanoramas.org/dem3/A37.zip
http://www.viewfinderpanoramas.org/dem3/A38.zip
http://www.viewfinderpanoramas.org/dem3/A43.zip
http://www.viewfinderpanoramas.org/dem3/A46.zip
http://www.viewfinderpanoramas.org/dem3/A47.zip
http://www.viewfinderpanoramas.org/dem3/A48.zip
http://www.viewfinderpanoramas.org/dem3/A49.zip
http://www.viewfinderpanoramas.org/dem3/A50.zip
http://www.viewfinderpanoramas.org/dem3/A51.zip
http://www.viewfinderpanoramas.org/dem3/A52.zip
http://www.viewfinderpanoramas.org/dem3/A53.zip
http://www.viewfinderpanoramas.org/dem3/AF3/N00E029.zip
http://www.viewfinderpanoramas.org/dem3/AF3/S01E037.zip
http://www.viewfinderpanoramas.org/dem3/AF3/S02E029.zip
http://www.viewfinderpanoramas.org/dem3/AF3/S04E036.zip
http://www.viewfinderpanoramas.org/dem3/AF3/S04E037.zip
http://www.viewfinderpanoramas.org/dem3/B28.zip
http://www.viewfinderpanoramas.org/dem3/B29.zip
http://www.viewfinderpanoramas.org/dem3/B30.zip
http://www.viewfinderpanoramas.org/dem3/B31.zip
http://www.viewfinderpanoramas.org/dem3/B32.zip
http://www.viewfinderpanoramas.org/dem3/B33.zip
http://www.viewfinderpanoramas.org/dem3/B34.zip
http://www.viewfinderpanoramas.org/dem3/B35.zip
http://www.viewfinderpanoramas.org/dem3/B36.zip
http://www.viewfinderpanoramas.org/dem3/B37.zip
http://www.viewfinderpanoramas.org/dem3/B38.zip
http://www.viewfinderpanoramas.org/dem3/B39.zip
http://www.viewfinderpanoramas.org/dem3/B43.zip
http://www.viewfinderpanoramas.org/dem3/B44.zip
http://www.viewfinderpanoramas.org/dem3/B46.zip
http://www.viewfinderpanoramas.org/dem3/B47.zip
http://www.viewfinderpanoramas.org/dem3/B48.zip
http://www.viewfinderpanoramas.org/dem3/B49.zip
http://www.viewfinderpanoramas.org/dem3/B50.zip
http://www.viewfinderpanoramas.org/dem3/B51.zip
http://www.viewfinderpanoramas.org/dem3/B52.zip
http://www.viewfinderpanoramas.org/dem3/BEAR.zip
http://www.viewfinderpanoramas.org/dem3/C18/N10W074.zip
http://www.viewfinderpanoramas.org/dem3/C18/N11W074.zip
http://www.viewfinderpanoramas.org/dem3/C28.zip
http://www.viewfinderpanoramas.org/dem3/C29.zip
http://www.viewfinderpanoramas.org/dem3/C30.zip
http://www.viewfinderpanoramas.org/dem3/C31.zip
http://www.viewfinderpanoramas.org/dem3/C32.zip
http://www.viewfinderpanoramas.org/dem3/C33.zip
http://www.viewfinderpanoramas.org/dem3/C34.zip
http://www.viewfinderpanoramas.org/dem3/C35.zip
http://www.viewfinderpanoramas.org/dem3/C36.zip
http://www.viewfinderpanoramas.org/dem3/C37.zip
http://www.viewfinderpanoramas.org/dem3/C38.zip
http://www.viewfinderpanoramas.org/dem3/C39.zip
http://www.viewfinderpanoramas.org/dem3/C43.zip
http://www.viewfinderpanoramas.org/dem3/C44.zip
http://www.viewfinderpanoramas.org/dem3/C46.zip
http://www.viewfinderpanoramas.org/dem3/C47.zip
http://www.viewfinderpanoramas.org/dem3/C48.zip
http://www.viewfinderpanoramas.org/dem3/C49.zip
http://www.viewfinderpanoramas.org/dem3/C50.zip
http://www.viewfinderpanoramas.org/dem3/C51.zip
http://www.viewfinderpanoramas.org/dem3/C52.zip
http://www.viewfinderpanoramas.org/dem3/D28.zip
http://www.viewfinderpanoramas.org/dem3/D29.zip
http://www.viewfinderpanoramas.org/dem3/D30.zip
http://www.viewfinderpanoramas.org/dem3/D31.zip
http://www.viewfinderpanoramas.org/dem3/D32.zip
http://www.viewfinderpanoramas.org/dem3/D33.zip
http://www.viewfinderpanoramas.org/dem3/D34.zip
http://www.viewfinderpanoramas.org/dem3/D35.zip
http://www.viewfinderpanoramas.org/dem3/D36.zip
http://www.viewfinderpanoramas.org/dem3/D37.zip
http://www.viewfinderpanoramas.org/dem3/D38.zip
http://www.viewfinderpanoramas.org/dem3/D39.zip
http://www.viewfinderpanoramas.org/dem3/D40.zip
http://www.viewfinderpanoramas.org/dem3/D43.zip
http://www.viewfinderpanoramas.org/dem3/D44.zip
http://www.viewfinderpanoramas.org/dem3/D46.zip
http://www.viewfinderpanoramas.org/dem3/D47.zip
http://www.viewfinderpanoramas.org/dem3/D48.zip
http://www.viewfinderpanoramas.org/dem3/D49.zip
http://www.viewfinderpanoramas.org/dem3/D50.zip
http://www.viewfinderpanoramas.org/dem3/D51.zip
http://www.viewfinderpanoramas.org/dem3/E28.zip
http://www.viewfinderpanoramas.org/dem3/E29.zip
http://www.viewfinderpanoramas.org/dem3/E30.zip
http://www.viewfinderpanoramas.org/dem3/E31.zip
http://www.viewfinderpanoramas.org/dem3/E32.zip
http://www.viewfinderpanoramas.org/dem3/E33.zip
http://www.viewfinderpanoramas.org/dem3/E34.zip
http://www.viewfinderpanoramas.org/dem3/E35.zip
http://www.viewfinderpanoramas.org/dem3/E36.zip
http://www.viewfinderpanoramas.org/dem3/E37.zip
http://www.viewfinderpanoramas.org/dem3/E38.zip
http://www.viewfinderpanoramas.org/dem3/E39.zip
http://www.viewfinderpanoramas.org/dem3/E40.zip
http://www.viewfinderpanoramas.org/dem3/E43.zip
http://www.viewfinderpanoramas.org/dem3/E44.zip
http://www.viewfinderpanoramas.org/dem3/E45.zip
http://www.viewfinderpanoramas.org/dem3/E46.zip
http://www.viewfinderpanoramas.org/dem3/E47.zip
http://www.viewfinderpanoramas.org/dem3/E48.zip
http://www.viewfinderpanoramas.org/dem3/E49.zip
http://www.viewfinderpanoramas.org/dem3/E50.zip
http://www.viewfinderpanoramas.org/dem3/E51.zip
http://www.viewfinderpanoramas.org/dem3/F28.zip
http://www.viewfinderpanoramas.org/dem3/F29.zip
http://www.viewfinderpanoramas.org/dem3/F30.zip
http://www.viewfinderpanoramas.org/dem3/F31.zip
http://www.viewfinderpanoramas.org/dem3/F32.zip
http://www.viewfinderpanoramas.org/dem3/F33.zip
http://www.viewfinderpanoramas.org/dem3/F34.zip
http://www.viewfinderpanoramas.org/dem3/F35.zip
http://www.viewfinderpanoramas.org/dem3/F36.zip
http://www.viewfinderpanoramas.org/dem3/F37.zip
http://www.viewfinderpanoramas.org/dem3/F38.zip
http://www.viewfinderpanoramas.org/dem3/F39.zip
http://www.viewfinderpanoramas.org/dem3/F40.zip
http://www.viewfinderpanoramas.org/dem3/F42.zip
http://www.viewfinderpanoramas.org/dem3/F43.zip
http://www.viewfinderpanoramas.org/dem3/F44.zip
http://www.viewfinderpanoramas.org/dem3/F45.zip
http://www.viewfinderpanoramas.org/dem3/F46.zip
http://www.viewfinderpanoramas.org/dem3/F47.zip
http://www.viewfinderpanoramas.org/dem3/F48.zip
http://www.viewfinderpanoramas.org/dem3/F49.zip
http://www.viewfinderpanoramas.org/dem3/F50.zip
http://www.viewfinderpanoramas.org/dem3/F51.zip
http://www.viewfinderpanoramas.org/dem3/FAR.zip
http://www.viewfinderpanoramas.org/dem3/FJ.zip
http://www.viewfinderpanoramas.org/dem3/G27.zip
http://www.viewfinderpanoramas.org/dem3/G28.zip
http://www.viewfinderpanoramas.org/dem3/G29.zip
http://www.viewfinderpanoramas.org/dem3/G30.zip
http://www.viewfinderpanoramas.org/dem3/G31.zip
http://www.viewfinderpanoramas.org/dem3/G32.zip
http://www.viewfinderpanoramas.org/dem3/G33.zip
http://www.viewfinderpanoramas.org/dem3/G34.zip
http://www.viewfinderpanoramas.org/dem3/G35.zip
http://www.viewfinderpanoramas.org/dem3/G36.zip
http://www.viewfinderpanoramas.org/dem3/G37.zip
http://www.viewfinderpanoramas.org/dem3/G38.zip
http://www.viewfinderpanoramas.org/dem3/G39.zip
http://www.viewfinderpanoramas.org/dem3/G40.zip
http://www.viewfinderpanoramas.org/dem3/G41.zip
http://www.viewfinderpanoramas.org/dem3/G42.zip
http://www.viewfinderpanoramas.org/dem3/G43.zip
http://www.viewfinderpanoramas.org/dem3/G44.zip
http://www.viewfinderpanoramas.org/dem3/G45.zip
http://www.viewfinderpanoramas.org/dem3/G46.zip
http://www.viewfinderpanoramas.org/dem3/G47.zip
http://www.viewfinderpanoramas.org/dem3/G48.zip
http://www.viewfinderpanoramas.org/dem3/G49.zip
http://www.viewfinderpanoramas.org/dem3/G50.zip
http://www.viewfinderpanoramas.org/dem3/G51.zip
http://www.viewfinderpanoramas.org/dem3/G52.zip
http://www.viewfinderpanoramas.org/dem3/G54.zip
http://www.viewfinderpanoramas.org/dem3/G56.zip
http://www.viewfinderpanoramas.org/dem3/H27.zip
http://www.viewfinderpanoramas.org/dem3/H28.zip
http://www.viewfinderpanoramas.org/dem3/H29.zip
http://www.viewfinderpanoramas.org/dem3/H30.zip
http://www.viewfinderpanoramas.org/dem3/H31.zip
http://www.viewfinderpanoramas.org/dem3/H32.zip
http://www.viewfinderpanoramas.org/dem3/H33.zip
http://www.viewfinderpanoramas.org/dem3/H34.zip
http://www.viewfinderpanoramas.org/dem3/H35.zip
http://www.viewfinderpanoramas.org/dem3/H36.zip
http://www.viewfinderpanoramas.org/dem3/H37.zip
http://www.viewfinderpanoramas.org/dem3/H38.zip
http://www.viewfinderpanoramas.org/dem3/H39.zip
http://www.viewfinderpanoramas.org/dem3/H40.zip
http://www.viewfinderpanoramas.org/dem3/H41.zip
http://www.viewfinderpanoramas.org/dem3/H42.zip
http://www.viewfinderpanoramas.org/dem3/H43.zip
http://www.viewfinderpanoramas.org/dem3/H44.zip
http://www.viewfinderpanoramas.org/dem3/H45.zip
http://www.viewfinderpanoramas.org/dem3/H46.zip
http://www.viewfinderpanoramas.org/dem3/H47.zip
http://www.viewfinderpanoramas.org/dem3/H48.zip
http://www.viewfinderpanoramas.org/dem3/H49.zip
http://www.viewfinderpanoramas.org/dem3/H50.zip
http://www.viewfinderpanoramas.org/dem3/H51.zip
http://www.viewfinderpanoramas.org/dem3/H52.zip
http://www.viewfinderpanoramas.org/dem3/H54.zip
http://www.viewfinderpanoramas.org/dem3/I28.zip
http://www.viewfinderpanoramas.org/dem3/I29.zip
http://www.viewfinderpanoramas.org/dem3/I30.zip
http://www.viewfinderpanoramas.org/dem3/I31.zip
http://www.viewfinderpanoramas.org/dem3/I32.zip
http://www.viewfinderpanoramas.org/dem3/I33.zip
http://www.viewfinderpanoramas.org/dem3/I34.zip
http://www.viewfinderpanoramas.org/dem3/I34/N35E023.zip
http://www.viewfinderpanoramas.org/dem3/I35.zip
http://www.viewfinderpanoramas.org/dem3/I36.zip
http://www.viewfinderpanoramas.org/dem3/I37.zip
http://www.viewfinderpanoramas.org/dem3/I38.zip
http://www.viewfinderpanoramas.org/dem3/I39.zip
http://www.viewfinderpanoramas.org/dem3/I40.zip
http://www.viewfinderpanoramas.org/dem3/I41.zip
http://www.viewfinderpanoramas.org/dem3/I42.zip
http://www.viewfinderpanoramas.org/dem3/I43.zip
http://www.viewfinderpanoramas.org/dem3/I44.zip
http://www.viewfinderpanoramas.org/dem3/I45.zip
http://www.viewfinderpanoramas.org/dem3/I46.zip
http://www.viewfinderpanoramas.org/dem3/I47.zip
http://www.viewfinderpanoramas.org/dem3/I48.zip
http://www.viewfinderpanoramas.org/dem3/I49.zip
http://www.viewfinderpanoramas.org/dem3/I50.zip
http://www.viewfinderpanoramas.org/dem3/I51.zip
http://www.viewfinderpanoramas.org/dem3/I52.zip
http://www.viewfinderpanoramas.org/dem3/I53.zip
http://www.viewfinderpanoramas.org/dem3/I54.zip
http://www.viewfinderpanoramas.org/dem3/ISL.zip
http://www.viewfinderpanoramas.org/dem3/J29.zip
http://www.viewfinderpanoramas.org/dem3/J30.zip
http://www.viewfinderpanoramas.org/dem3/J31.zip
http://www.viewfinderpanoramas.org/dem3/J32.zip
http://www.viewfinderpanoramas.org/dem3/J34.zip
http://www.viewfinderpanoramas.org/dem3/J36.zip
http://www.viewfinderpanoramas.org/dem3/J37.zip
http://www.viewfinderpanoramas.org/dem3/J38.zip
http://www.viewfinderpanoramas.org/dem3/J39.zip
http://www.viewfinderpanoramas.org/dem3/J40.zip
http://www.viewfinderpanoramas.org/dem3/J41.zip
http://www.viewfinderpanoramas.org/dem3/J42.zip
http://www.viewfinderpanoramas.org/dem3/J43.zip
http://www.viewfinderpanoramas.org/dem3/J44.zip
http://www.viewfinderpanoramas.org/dem3/J45.zip
http://www.viewfinderpanoramas.org/dem3/J46.zip
http://www.viewfinderpanoramas.org/dem3/J47.zip
http://www.viewfinderpanoramas.org/dem3/J48.zip
http://www.viewfinderpanoramas.org/dem3/J49.zip
http://www.viewfinderpanoramas.org/dem3/J50.zip
http://www.viewfinderpanoramas.org/dem3/J51.zip
http://www.viewfinderpanoramas.org/dem3/J52.zip
http://www.viewfinderpanoramas.org/dem3/J53.zip
http://www.viewfinderpanoramas.org/dem3/J53/N36E137.zip
http://www.viewfinderpanoramas.org/dem3/J54.zip
http://www.viewfinderpanoramas.org/dem3/JANMAYEN.zip
http://www.viewfinderpanoramas.org/dem3/K30.zip
http://www.viewfinderpanoramas.org/dem3/K30/N42E001.zip
http://www.viewfinderpanoramas.org/dem3/K31/N42E000.zip
http://www.viewfinderpanoramas.org/dem3/K31/N42E001.zip
http://www.viewfinderpanoramas.org/dem3/K32/N42E008.zip
http://www.viewfinderpanoramas.org/dem3/K32/N43E006.zip
http://www.viewfinderpanoramas.org/dem3/K32/N43E007.zip
http://www.viewfinderpanoramas.org/dem3/K33/N42E013.zip
http://www.viewfinderpanoramas.org/dem3/K34.zip
http://www.viewfinderpanoramas.org/dem3/K36.zip
http://www.viewfinderpanoramas.org/dem3/K37.zip
http://www.viewfinderpanoramas.org/dem3/K38.zip
http://www.viewfinderpanoramas.org/dem3/K39.zip
http://www.viewfinderpanoramas.org/dem3/K40.zip
http://www.viewfinderpanoramas.org/dem3/K41.zip
http://www.viewfinderpanoramas.org/dem3/K42.zip
http://www.viewfinderpanoramas.org/dem3/K43.zip
http://www.viewfinderpanoramas.org/dem3/K44.zip
http://www.viewfinderpanoramas.org/dem3/K45.zip
http://www.viewfinderpanoramas.org/dem3/K46.zip
http://www.viewfinderpanoramas.org/dem3/K47.zip
http://www.viewfinderpanoramas.org/dem3/K48.zip
http://www.viewfinderpanoramas.org/dem3/K49.zip
http://www.viewfinderpanoramas.org/dem3/K50.zip
http://www.viewfinderpanoramas.org/dem3/K51.zip
http://www.viewfinderpanoramas.org/dem3/K52.zip
http://www.viewfinderpanoramas.org/dem3/K53.zip
http://www.viewfinderpanoramas.org/dem3/K54.zip
http://www.viewfinderpanoramas.org/dem3/K55.zip
http://www.viewfinderpanoramas.org/dem3/L31/N44E005.zip
http://www.viewfinderpanoramas.org/dem3/L31/N45E005.zip
http://www.viewfinderpanoramas.org/dem3/L32/N44E006.zip
http://www.viewfinderpanoramas.org/dem3/L32/N44E007.zip
http://www.viewfinderpanoramas.org/dem3/L32/n44e010.zip
http://www.viewfinderpanoramas.org/dem3/L32/N45E006.zip
http://www.viewfinderpanoramas.org/dem3/L32/N45E007.zip
http://www.viewfinderpanoramas.org/dem3/L32/N45E008.zip
http://www.viewfinderpanoramas.org/dem3/L32/N45E009.zip
http://www.viewfinderpanoramas.org/dem3/L32/N45E010.zip
http://www.viewfinderpanoramas.org/dem3/L32/N45E011.zip
http://www.viewfinderpanoramas.org/dem3/L32/N46E006.zip
http://www.viewfinderpanoramas.org/dem3/L32/N46E007.zip
http://www.viewfinderpanoramas.org/dem3/L32/N46E008.zip
http://www.viewfinderpanoramas.org/dem3/L32/N46E009.zip
http://www.viewfinderpanoramas.org/dem3/L32/N46E010.zip
http://www.viewfinderpanoramas.org/dem3/L32/N46E011.zip
http://www.viewfinderpanoramas.org/dem3/L32/N47E008.zip
http://www.viewfinderpanoramas.org/dem3/L32/N47E009.zip
http://www.viewfinderpanoramas.org/dem3/L32/N47E010.zip
http://www.viewfinderpanoramas.org/dem3/L32/N47E011.zip
http://www.viewfinderpanoramas.org/dem3/L33/N45E012.zip
http://www.viewfinderpanoramas.org/dem3/L33/N46E012.zip
http://www.viewfinderpanoramas.org/dem3/L33/N46E013.zip
http://www.viewfinderpanoramas.org/dem3/L33/N46E014.zip
http://www.viewfinderpanoramas.org/dem3/L33/N46E015.zip
http://www.viewfinderpanoramas.org/dem3/L33/N47E012.zip
http://www.viewfinderpanoramas.org/dem3/L33/N47E013.zip
http://www.viewfinderpanoramas.org/dem3/L33/N47E014.zip
http://www.viewfinderpanoramas.org/dem3/L33/N47E015.zip
http://www.viewfinderpanoramas.org/dem3/M34/N49E019.zip
http://www.viewfinderpanoramas.org/dem3/M34/N49E020.zip
http://www.viewfinderpanoramas.org/dem3/MAUR.zip
http://www.viewfinderpanoramas.org/dem3/NMB.zip
http://www.viewfinderpanoramas.org/dem3/O59/N59E170.zip
http://www.viewfinderpanoramas.org/dem3/P02.zip
http://www.viewfinderpanoramas.org/dem3/P31v2.zip
http://www.viewfinderpanoramas.org/dem3/P32v2.zip
http://www.viewfinderpanoramas.org/dem3/P33v2.zip
http://www.viewfinderpanoramas.org/dem3/P34v2.zip
http://www.viewfinderpanoramas.org/dem3/P35v2.zip
http://www.viewfinderpanoramas.org/dem3/P36v2.zip
http://www.viewfinderpanoramas.org/dem3/P37v2.zip
http://www.viewfinderpanoramas.org/dem3/P38v2.zip
http://www.viewfinderpanoramas.org/dem3/P39v2.zip
http://www.viewfinderpanoramas.org/dem3/P40v2.zip
http://www.viewfinderpanoramas.org/dem3/P41.zip
http://www.viewfinderpanoramas.org/dem3/P42.zip
http://www.viewfinderpanoramas.org/dem3/P43.zip
http://www.viewfinderpanoramas.org/dem3/P44.zip
http://www.viewfinderpanoramas.org/dem3/P45.zip
http://www.viewfinderpanoramas.org/dem3/P46.zip
http://www.viewfinderpanoramas.org/dem3/P47.zip
http://www.viewfinderpanoramas.org/dem3/P48.zip
http://www.viewfinderpanoramas.org/dem3/P49.zip
http://www.viewfinderpanoramas.org/dem3/P50.zip
http://www.viewfinderpanoramas.org/dem3/P51.zip
http://www.viewfinderpanoramas.org/dem3/P52.zip
http://www.viewfinderpanoramas.org/dem3/P53.zip
http://www.viewfinderpanoramas.org/dem3/P54.zip
http://www.viewfinderpanoramas.org/dem3/P55.zip
http://www.viewfinderpanoramas.org/dem3/P56.zip
http://www.viewfinderpanoramas.org/dem3/P57.zip
http://www.viewfinderpanoramas.org/dem3/P58.zip
http://www.viewfinderpanoramas.org/dem3/P59.zip
http://www.viewfinderpanoramas.org/dem3/P60.zip
http://www.viewfinderpanoramas.org/dem3/Q01.zip
http://www.viewfinderpanoramas.org/dem3/Q02.zip
http://www.viewfinderpanoramas.org/dem3/Q32v2.zip
http://www.viewfinderpanoramas.org/dem3/Q33v2.zip
http://www.viewfinderpanoramas.org/dem3/Q34v2.zip
http://www.viewfinderpanoramas.org/dem3/Q35v2.zip
http://www.viewfinderpanoramas.org/dem3/Q36v2.zip
http://www.viewfinderpanoramas.org/dem3/Q37v2.zip
http://www.viewfinderpanoramas.org/dem3/Q38v2.zip
http://www.viewfinderpanoramas.org/dem3/Q39v2.zip
http://www.viewfinderpanoramas.org/dem3/Q40v2.zip
http://www.viewfinderpanoramas.org/dem3/Q41.zip
http://www.viewfinderpanoramas.org/dem3/Q42.zip
http://www.viewfinderpanoramas.org/dem3/Q43.zip
http://www.viewfinderpanoramas.org/dem3/Q44.zip
http://www.viewfinderpanoramas.org/dem3/Q45.zip
http://www.viewfinderpanoramas.org/dem3/Q46.zip
http://www.viewfinderpanoramas.org/dem3/Q47.zip
http://www.viewfinderpanoramas.org/dem3/Q48.zip
http://www.viewfinderpanoramas.org/dem3/Q49.zip
http://www.viewfinderpanoramas.org/dem3/Q50.zip
http://www.viewfinderpanoramas.org/dem3/Q51.zip
http://www.viewfinderpanoramas.org/dem3/Q52.zip
http://www.viewfinderpanoramas.org/dem3/Q53.zip
http://www.viewfinderpanoramas.org/dem3/Q54.zip
http://www.viewfinderpanoramas.org/dem3/Q55.zip
http://www.viewfinderpanoramas.org/dem3/Q56.zip
http://www.viewfinderpanoramas.org/dem3/Q57.zip
http://www.viewfinderpanoramas.org/dem3/Q58.zip
http://www.viewfinderpanoramas.org/dem3/Q59.zip
http://www.viewfinderpanoramas.org/dem3/Q60.zip
http://www.viewfinderpanoramas.org/dem3/R01.zip
http://www.viewfinderpanoramas.org/dem3/R33v2.zip
http://www.viewfinderpanoramas.org/dem3/R34v2.zip
http://www.viewfinderpanoramas.org/dem3/R35v2.zip
http://www.viewfinderpanoramas.org/dem3/R36v2.zip
http://www.viewfinderpanoramas.org/dem3/R37v2.zip
http://www.viewfinderpanoramas.org/dem3/R38v2.zip
http://www.viewfinderpanoramas.org/dem3/R39.zip
http://www.viewfinderpanoramas.org/dem3/R40.zip
http://www.viewfinderpanoramas.org/dem3/R41.zip
http://www.viewfinderpanoramas.org/dem3/R42.zip
http://www.viewfinderpanoramas.org/dem3/R43.zip
http://www.viewfinderpanoramas.org/dem3/R44.zip
http://www.viewfinderpanoramas.org/dem3/R45.zip
http://www.viewfinderpanoramas.org/dem3/R46.zip
http://www.viewfinderpanoramas.org/dem3/R47.zip
http://www.viewfinderpanoramas.org/dem3/R48.zip
http://www.viewfinderpanoramas.org/dem3/R49.zip
http://www.viewfinderpanoramas.org/dem3/R50.zip
http://www.viewfinderpanoramas.org/dem3/R51.zip
http://www.viewfinderpanoramas.org/dem3/R52.zip
http://www.viewfinderpanoramas.org/dem3/R53.zip
http://www.viewfinderpanoramas.org/dem3/R54.zip
http://www.viewfinderpanoramas.org/dem3/R55.zip
http://www.viewfinderpanoramas.org/dem3/R56.zip
http://www.viewfinderpanoramas.org/dem3/R57.zip
http://www.viewfinderpanoramas.org/dem3/R58.zip
http://www.viewfinderpanoramas.org/dem3/R59.zip
http://www.viewfinderpanoramas.org/dem3/R60.zip
http://www.viewfinderpanoramas.org/dem3/REU.zip
http://www.viewfinderpanoramas.org/dem3/S39.zip
http://www.viewfinderpanoramas.org/dem3/S40.zip
http://www.viewfinderpanoramas.org/dem3/S41.zip
http://www.viewfinderpanoramas.org/dem3/S42.zip
http://www.viewfinderpanoramas.org/dem3/S43.zip
http://www.viewfinderpanoramas.org/dem3/S44.zip
http://www.viewfinderpanoramas.org/dem3/S45.zip
http://www.viewfinderpanoramas.org/dem3/S46.zip
http://www.viewfinderpanoramas.org/dem3/S47.zip
http://www.viewfinderpanoramas.org/dem3/S48.zip
http://www.viewfinderpanoramas.org/dem3/S49.zip
http://www.viewfinderpanoramas.org/dem3/S50.zip
http://www.viewfinderpanoramas.org/dem3/S51.zip
http://www.viewfinderpanoramas.org/dem3/S52.zip
http://www.viewfinderpanoramas.org/dem3/S53.zip
http://www.viewfinderpanoramas.org/dem3/S54.zip
http://www.viewfinderpanoramas.org/dem3/S55.zip
http://www.viewfinderpanoramas.org/dem3/S56.zip
http://www.viewfinderpanoramas.org/dem3/SA31.zip
http://www.viewfinderpanoramas.org/dem3/SA32.zip
http://www.viewfinderpanoramas.org/dem3/SA33.zip
http://www.viewfinderpanoramas.org/dem3/SA34.zip
http://www.viewfinderpanoramas.org/dem3/SA35.zip
http://www.viewfinderpanoramas.org/dem3/SA36.zip
http://www.viewfinderpanoramas.org/dem3/SA37.zip
http://www.viewfinderpanoramas.org/dem3/SA38.zip
http://www.viewfinderpanoramas.org/dem3/SA40.zip
http://www.viewfinderpanoramas.org/dem3/SA43.zip
http://www.viewfinderpanoramas.org/dem3/SA47.zip
http://www.viewfinderpanoramas.org/dem3/SA48.zip
http://www.viewfinderpanoramas.org/dem3/SA49.zip
http://www.viewfinderpanoramas.org/dem3/SA50.zip
http://www.viewfinderpanoramas.org/dem3/SA51.zip
http://www.viewfinderpanoramas.org/dem3/SA52.zip
http://www.viewfinderpanoramas.org/dem3/SA53.zip
http://www.viewfinderpanoramas.org/dem3/SA54.zip
http://www.viewfinderpanoramas.org/dem3/SA55.zip
http://www.viewfinderpanoramas.org/dem3/SA56.zip
http://www.viewfinderpanoramas.org/dem3/SB32.zip
http://www.viewfinderpanoramas.org/dem3/SB33.zip
http://www.viewfinderpanoramas.org/dem3/SB34.zip
http://www.viewfinderpanoramas.org/dem3/SB35.zip
http://www.viewfinderpanoramas.org/dem3/SB36.zip
http://www.viewfinderpanoramas.org/dem3/SB37.zip
http://www.viewfinderpanoramas.org/dem3/SB39.zip
http://www.viewfinderpanoramas.org/dem3/SB40.zip
http://www.viewfinderpanoramas.org/dem3/SB42.zip
http://www.viewfinderpanoramas.org/dem3/SB43.zip
http://www.viewfinderpanoramas.org/dem3/SB47.zip
http://www.viewfinderpanoramas.org/dem3/SB48.zip
http://www.viewfinderpanoramas.org/dem3/SB49.zip
http://www.viewfinderpanoramas.org/dem3/SB50.zip
http://www.viewfinderpanoramas.org/dem3/SB51.zip
http://www.viewfinderpanoramas.org/dem3/SB52.zip
http://www.viewfinderpanoramas.org/dem3/SB53.zip
http://www.viewfinderpanoramas.org/dem3/SB54.zip
http://www.viewfinderpanoramas.org/dem3/SB55.zip
http://www.viewfinderpanoramas.org/dem3/SB56.zip
http://www.viewfinderpanoramas.org/dem3/SB57.zip
http://www.viewfinderpanoramas.org/dem3/SC3.zip
http://www.viewfinderpanoramas.org/dem3/SC18/S09W078.zip
http://www.viewfinderpanoramas.org/dem3/SC18/S10W078.zip
http://www.viewfinderpanoramas.org/dem3/SC18/S11W076.zip
http://www.viewfinderpanoramas.org/dem3/SC18/S11W077.zip
http://www.viewfinderpanoramas.org/dem3/SC18/S11W078.zip
http://www.viewfinderpanoramas.org/dem3/SC18/S12W075.zip
http://www.viewfinderpanoramas.org/dem3/SC18/S12W076.zip
http://www.viewfinderpanoramas.org/dem3/SC18/S12W077.zip
http://www.viewfinderpanoramas.org/dem3/SC33.zip
http://www.viewfinderpanoramas.org/dem3/SC34.zip
http://www.viewfinderpanoramas.org/dem3/SC35.zip
http://www.viewfinderpanoramas.org/dem3/SC36.zip
http://www.viewfinderpanoramas.org/dem3/SC37.zip
http://www.viewfinderpanoramas.org/dem3/SC38.zip
http://www.viewfinderpanoramas.org/dem3/SC39.zip
http://www.viewfinderpanoramas.org/dem3/SC40.zip
http://www.viewfinderpanoramas.org/dem3/SC49.zip
http://www.viewfinderpanoramas.org/dem3/SC50.zip
http://www.viewfinderpanoramas.org/dem3/SC51.zip
http://www.viewfinderpanoramas.org/dem3/SC52.zip
http://www.viewfinderpanoramas.org/dem3/SC53.zip
http://www.viewfinderpanoramas.org/dem3/SC54.zip
http://www.viewfinderpanoramas.org/dem3/SC55.zip
http://www.viewfinderpanoramas.org/dem3/SC56.zip
http://www.viewfinderpanoramas.org/dem3/SC57.zip
http://www.viewfinderpanoramas.org/dem3/SD18/S13W076.zip
http://www.viewfinderpanoramas.org/dem3/SD18/S14W073.zip
http://www.viewfinderpanoramas.org/dem3/SD18/S14W074.zip
http://www.viewfinderpanoramas.org/dem3/SD19/S14W071.zip
http://www.viewfinderpanoramas.org/dem3/SD19/S14W072.zip
http://www.viewfinderpanoramas.org/dem3/SD19/S16W069.zip
http://www.viewfinderpanoramas.org/dem3/SD32.zip
http://www.viewfinderpanoramas.org/dem3/SD33.zip
http://www.viewfinderpanoramas.org/dem3/SD34.zip
http://www.viewfinderpanoramas.org/dem3/SD35.zip
http://www.viewfinderpanoramas.org/dem3/SD36.zip
http://www.viewfinderpanoramas.org/dem3/SD37.zip
http://www.viewfinderpanoramas.org/dem3/SD38.zip
http://www.viewfinderpanoramas.org/dem3/SD39.zip
http://www.viewfinderpanoramas.org/dem3/SD40.zip
http://www.viewfinderpanoramas.org/dem3/SE19/S17W068.zip
http://www.viewfinderpanoramas.org/dem3/SE19/S17W069.zip
http://www.viewfinderpanoramas.org/dem3/SE32.zip
http://www.viewfinderpanoramas.org/dem3/SE33.zip
http://www.viewfinderpanoramas.org/dem3/SE34.zip
http://www.viewfinderpanoramas.org/dem3/SE35.zip
http://www.viewfinderpanoramas.org/dem3/SE36.zip
http://www.viewfinderpanoramas.org/dem3/SE37.zip
http://www.viewfinderpanoramas.org/dem3/SE38.zip
http://www.viewfinderpanoramas.org/dem3/SE39.zip
http://www.viewfinderpanoramas.org/dem3/SE40.zip
http://www.viewfinderpanoramas.org/dem3/SE41.zip
http://www.viewfinderpanoramas.org/dem3/SF33.zip
http://www.viewfinderpanoramas.org/dem3/SF34.zip
http://www.viewfinderpanoramas.org/dem3/SF35.zip
http://www.viewfinderpanoramas.org/dem3/SF36.zip
http://www.viewfinderpanoramas.org/dem3/SF37.zip
http://www.viewfinderpanoramas.org/dem3/SF38.zip
http://www.viewfinderpanoramas.org/dem3/SF39.zip
http://www.viewfinderpanoramas.org/dem3/SF40.zip
http://www.viewfinderpanoramas.org/dem3/SG.zip
http://www.viewfinderpanoramas.org/dem3/SG33.zip
http://www.viewfinderpanoramas.org/dem3/SG34.zip
http://www.viewfinderpanoramas.org/dem3/SG35.zip
http://www.viewfinderpanoramas.org/dem3/SG36.zip
http://www.viewfinderpanoramas.org/dem3/SG38.zip
http://www.viewfinderpanoramas.org/dem3/SH19/S32W070.zip
http://www.viewfinderpanoramas.org/dem3/SH19/S32W071.zip
http://www.viewfinderpanoramas.org/dem3/SH33.zip
http://www.viewfinderpanoramas.org/dem3/SH34.zip
http://www.viewfinderpanoramas.org/dem3/SH35.zip
http://www.viewfinderpanoramas.org/dem3/SH36.zip
http://www.viewfinderpanoramas.org/dem3/SHL.zip
http://www.viewfinderpanoramas.org/dem3/SI19/S33W070.zip
http://www.viewfinderpanoramas.org/dem3/SI19/S33W071.zip
http://www.viewfinderpanoramas.org/dem3/SI19/S34W070.zip
http://www.viewfinderpanoramas.org/dem3/SI19/S34W071.zip
http://www.viewfinderpanoramas.org/dem3/SI33.zip
http://www.viewfinderpanoramas.org/dem3/SI34.zip
http://www.viewfinderpanoramas.org/dem3/SI35.zip
http://www.viewfinderpanoramas.org/dem3/SI59.zip
http://www.viewfinderpanoramas.org/dem3/SI60.zip
http://www.viewfinderpanoramas.org/dem3/SJ59.zip
http://www.viewfinderpanoramas.org/dem3/SJ60.zip
http://www.viewfinderpanoramas.org/dem3/SK18.zip
http://www.viewfinderpanoramas.org/dem3/SK19.zip
http://www.viewfinderpanoramas.org/dem3/SK59.zip
http://www.viewfinderpanoramas.org/dem3/SK59/S44E169.zip
http://www.viewfinderpanoramas.org/dem3/SK59/S44E170.zip
http://www.viewfinderpanoramas.org/dem3/SK59/S44E171.zip
http://www.viewfinderpanoramas.org/dem3/SK60.zip
http://www.viewfinderpanoramas.org/dem3/SL18.zip
http://www.viewfinderpanoramas.org/dem3/SL19.zip
http://www.viewfinderpanoramas.org/dem3/SL58.zip
http://www.viewfinderpanoramas.org/dem3/SL58/S45E167.zip
http://www.viewfinderpanoramas.org/dem3/SL58/S46E166.zip
http://www.viewfinderpanoramas.org/dem3/SL58/S46E167.zip
http://www.viewfinderpanoramas.org/dem3/SL59.zip
http://www.viewfinderpanoramas.org/dem3/SL59/S45E168.zip
http://www.viewfinderpanoramas.org/dem3/SL59/S45E169.zip
http://www.viewfinderpanoramas.org/dem3/SM18.zip
http://www.viewfinderpanoramas.org/dem3/SM19.zip
http://www.viewfinderpanoramas.org/dem3/SN18.zip
http://www.viewfinderpanoramas.org/dem3/SN19.zip
http://www.viewfinderpanoramas.org/dem3/SV.zip
http://www.viewfinderpanoramas.org/dem3/T40.zip
http://www.viewfinderpanoramas.org/dem3/T41.zip
http://www.viewfinderpanoramas.org/dem3/T42.zip
http://www.viewfinderpanoramas.org/dem3/T43.zip
http://www.viewfinderpanoramas.org/dem3/T44.zip
http://www.viewfinderpanoramas.org/dem3/T45.zip
http://www.viewfinderpanoramas.org/dem3/T46.zip
http://www.viewfinderpanoramas.org/dem3/T47.zip
http://www.viewfinderpanoramas.org/dem3/T48.zip
http://www.viewfinderpanoramas.org/dem3/T49.zip
http://www.viewfinderpanoramas.org/dem3/T53.zip
http://www.viewfinderpanoramas.org/dem3/T54.zip
http://www.viewfinderpanoramas.org/dem3/T55.zip
http://www.viewfinderpanoramas.org/dem3/T56.zip
http://www.viewfinderpanoramas.org/dem3/TAH.zip
http://www.viewfinderpanoramas.org/dem3/TWN.zip
http://www.viewfinderpanoramas.org/dem3/U44.zip
http://www.viewfinderpanoramas.org/dem3/U46.zip
http://www.viewfinderpanoramas.org/dem3/U47.zip
'''

if __name__ == '__main__':

    out = writer(stdout, dialect='excel-tab')
    out.writerow(('name', 'path', 'url'))

    for url in zip_urls.split():
        if not url.endswith('.zip'):
            continue
    
        try:
            zip = ZipFile(RemoteFileObject(url, verbose=False))
        except BadZipfile:
            print >> stderr, '---- bad ----', url
            continue
        else:
            print >> stderr, url
        
        for path in zip.namelist():
            if basename(path):
                out.writerow((basename(path), path, url))

