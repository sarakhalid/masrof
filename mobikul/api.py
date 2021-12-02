apis={
    'homepage':{
				'description':'HomePage API',
				'uri':'/mobikul/homepage',
                'request':['POST']
			},

    'splashPageData':{
                'description':'Default data to saved at app end.',
                'uri':'/mobikul/splashPageData',
                'request':['POST']
            },

    'sliderProducts':{
                'description':'Product(s) of given Product Slider Record',
                'uri':'/mobikul/sliderProducts/<int:product_slider_id>;',
                'request':['POST']
            },

    'sliderProducts':{
                'description':'Product(s) of given Product Slider Record',
                'uri':'/mobikul/search',
                'request':['POST'],
                'body':{
                        "search":"l",
                         "offset":25
                        }
            },

    'MyOrders':{
                'description':'',
                'uri':'/mobikul/my/orders',
                'request':['POST'],

            },

    'MyOrderDetail':{
                'description':'',
                'uri':'/mobikul/my/order/<int:order_id>',
                'request':['POST'],
            },
    'removeWishlist': {
        'description': '',
        'uri': '/mobikul/my/removeWishlist/<int:wishlist_id>',
        'request': ['DELETE'],
    },


    'MyAddress':{
                'description':'',
                'uri':'/mobikul/my/addresses',
                'request':['POST'],
            },
            
    'setMyDefaultAddress':{
                'description':'',
                'uri':'/mobikul/my/address/default/<int:addressId>',
                'request':['PUT'],
            },

    'addMyNewAddress':{
                'description':'',
                'uri':'/mobikul/my/address/new',
                'request':['POST'],
                'body':{
                    "name":"acdef",
                    "city":"xyz",
                    "zip":"0987456",
                    "street":"lmno",
                    "phone":"1236547890",
                    "county_id":"3",
                    "state_id" :"5"
                }
            },

    'editAddressDetail':{
                'description':'',
                'uri':'/mobikul/my/address/<int:address_id>',
                'request':['POST','PUT','DELETE'],
                'body':{
                    "name":"acdef",
                    "city":"xyz",
                    "zip":"0987456",
                    "street":"lmno",
                    "phone":"1236547890",
                    "county_id":"3",
                    "state_id" :"5"
                }
            },

    'myAccount':{
                'description':'',
                'uri':'/mobikul/my/account',
                'request':['POST'],
            },

            
    'localizationData':{
                'description':'',
                'uri':'/mobikul/localizationData',
                'request':['POST'],
            },

    'myCartDetails':{
                'description':'',
                'uri':'/mobikul/mycart',
                'request':['POST'],
            },

    'editCartDetail':{
                'description':'',
                'uri':'/mobikul/mycart/<int:line_id>',
                'request':['POST','PUT','DELETE'],
                'body':{
                    'set_qty':"3",
                    'add_qty':"3"
                }
            },

    'emptyCart':{
                'description':'',
                'uri':'/mobikul/mycart/setToEmpty',
                'request':['DELETE'],
                'body':{
                    'set_qty':"3",
                    'add_qty':"3"
                }
            },

    'addToCart':{
                'description':'',
                'uri':'/mobikul/mycart/addToCart',
                'request':['POST'],
                'body':{
                    'productId':"16",
                    'set_qty':"3",
                    'add_qty':"3"
                }
            },

    'paymentAcquirers':{
                'description':'',
                'uri':'/mobikul/paymentAcquirers',
                'request':['POST'],
                
            },

    'orderReviewData':{
                'description':'',
                'uri':'/mobikul/orderReviewData',
                'request':['POST'],
                'body':{
                        "acquirerId":"1",
                        "shippingAddressId":"5"
                    }
            },

    'placeMyOrders':{
                'description':'',
                'uri':'/mobikul/placeMyOrder',
                'request':['POST'],
                
            },

            
    'signUp':{
                'description':'',
                'uri':'/mobikul/customer/signUp',
                'request':['POST'],
                'body':{
                    "name":"Saurabh Gupta",
                    "login":"saurabh.gupta781@webkul.com",
                    "password":"123"
                }
                
            },

    'login':{
                'description':'',
                'uri':'/mobikul/customer/login',
                'request':['POST'],
            },
    
    'signOut':{
                'description':'',
                'uri':'/mobikul/customer/signOut',
                'request':['POST'],
            },

    
    'resetPassword':{
                'description':'',
                'uri':'/mobikul/customer/resetPassword',
                'request':['POST'],
                'body':{
                    "name":"Saurabh Gupta",
                    "login":"saurabh.gupta781@webkul.com",
                    "password":123
                    }
            },

    'signUp':{
                'description':'',
                'uri':'/mobikul/customer/signUp',
                'request':['POST'],
                'body':{
                    "name":"Saurabh Gupta",
                    "login":"saurabh.gupta781@webkul.com",
                    "password":123
                    }
            },


}


