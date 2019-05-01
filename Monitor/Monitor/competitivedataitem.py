# Author: AADHIKARI - 06/03/2018
import scrapy

class CompetitiveDataItem(scrapy.Item):
	unique_id			= scrapy.Field()
	md5_url				= scrapy.Field()
	collection_date			= scrapy.Field()
	pickup_date			= scrapy.Field()
	drop_date			= scrapy.Field()
	pickup_time			= scrapy.Field()
	drop_time			= scrapy.Field()
	trip_type			= scrapy.Field()
	vendor				= scrapy.Field()
	src_city			= scrapy.Field()
	dst_city			= scrapy.Field()
	cab_type			= scrapy.Field()
	normalized_cab_type 		= scrapy.Field()
	cab_name			= scrapy.Field()
	pax_count			= scrapy.Field()
	markup_price			= scrapy.Field()
	base_price			= scrapy.Field()
	toll				= scrapy.Field()
	toll_included			= scrapy.Field()
	gst				= scrapy.Field()
	gst_included			= scrapy.Field()
	free_cancelation		= scrapy.Field()
	cancellation_charge		= scrapy.Field()
	coupon				= scrapy.Field()
	poll_priority			= scrapy.Field()
	url				= scrapy.Field()
	
	
	
		
		
	
	
	
	
