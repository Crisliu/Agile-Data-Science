db.on_time_performance.findOne({Carrier: 'DL', FlightDate: '2015-01-01', FlightNum: 478})

db.on_time_performance.ensureIndex({Carrier: 1, FlightDate: 1, FlightNum: 1})

db.on_time_performance.findOne({Carrier: 'DL', FlightDate: '2015-01-01', FlightNum: 478})