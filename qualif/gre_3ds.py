import geo.grenoble

m3 = geo.grenoble.list_nodes("m3")
a8 = geo.grenoble.list_nodes("a8")
wsn430 = geo.grenoble.list_nodes("wsn430")
geo.grenoble.dump3ds("m3", m3)
geo.grenoble.dump3ds("a8", a8)
geo.grenoble.dump3ds("wsn430", wsn430)
