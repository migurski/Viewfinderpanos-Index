Viewfinder Panoramas Index
==========================

Minimal HTTP redirect application required to correctly retrieve 1°×1° degree digital elevaltion models from the Viewfinder Panoramas project.

More information about the project:

* [ Completing The Worldwide Elevation Map ]( http://www.viewfinderpanoramas.org/topog.html )
* [ Digital Elevation Data ]( http://www.viewfinderpanoramas.org/dem3/DEM3-ReadMe.html )
* [ Coverage Map ]( http://www.viewfinderpanoramas.org/Coverage%20map%20viewfinderpanoramas_org3.htm )

Index collected August, 2012 using `viewfinderpanoramas-catalog.py` script.

The application is currently deployed to Heroku and can be used directly via [viewfinderpanos-index.herokuapp.com]( http://viewfinderpanos-index.herokuapp.com/index.php/S55W036.hgt ).

Using The Index
---------------

Determine your 1°×1° degree area of coverage. Digital elevation files are numbered from the lower-left corner and follow a predictable naming pattern. Some examples:

*  37.804317, -122.271169 = `N37W123.hgt`
*  52.514549,   13.350095 = `N52E013.hgt`
* -22.951913,  -43.210462 = `S23W044.hgt`
* -25.344957,  131.034966 = `S26E131.hgt`

Request the [HGT]( http://www2.jpl.nasa.gov/srtm/faq.html ) file with a URL like `http://viewfinderpanos-index.herokuapp.com/index.php/N47E011.hgt`.

Watch for one of two HTTP response codes: `404` for height files missing from the [Coverage Map]( http://www.viewfinderpanoramas.org/Coverage%20map%20viewfinderpanoramas_org3.htm ), `302` for existing data. Additionally look for two HTTP headers: `Location` for the URL of the needed Zip archive, and `X-Zip-Path` for the path to the elevation quad within the archive.

Examples
--------

Existing data:

    % curl -is http://viewfinderpanos-index.herokuapp.com/index.php/N47E011.hgt
      
      HTTP/1.1 302 Found
      Content-Type: text/plain
      Location: http://www.viewfinderpanoramas.org/dem3/L32/N47E011.zip
      X-Zip-Path: N47E011.hgt
      Content-Length: 56
      
      http://www.viewfinderpanoramas.org/dem3/L32/N47E011.zip

Nonexistent data:

    % curl -is http://viewfinderpanos-index.herokuapp.com/index.php/N37W123.hgt
      
      HTTP/1.1 404 Not Found
      Content-Type: text/plain
      Content-Length: 7
      
      Sorry.
