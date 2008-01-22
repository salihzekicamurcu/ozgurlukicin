from django.conf.urls.defaults import *
from oi.sanat.feeds import *

feed_dict = {
             'rss': Tema_RSS,
             'atom': Tema_Atom,
            }

urlpatterns = patterns ('oi.sanat.views',
	 					#the first page listing
						(r'^goster/(?P<sort_by>[a-z]+)/$','list_material'),
						(r'^kategori/(?P<cat_name>[a-z]+)/$','list_category'),
		  				(r'^dosya/(?P<file_id>[0-9]+)/$','file_detail'),
						(r'^kullanici/(?P<username>[a-z]+)/$','list_user'),
		  				(r'^oy/$','vote_it'),
                        (r'^ekle/$','add_file'),
                        
                        
)

urlpatterns+=patterns('',
        #the rss feeds
        (r'^(?P<url>.*)/yeni/$', 'django.contrib.syndication.views.feed', {'feed_dict': feed_dict}),
        
        )
