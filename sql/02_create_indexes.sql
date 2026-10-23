CREATE INDEX IF NOT EXISTS idx_shipments_date ON shipments(Shipment_Date);
CREATE INDEX IF NOT EXISTS idx_shipments_region ON shipments(Destination_Region,Delivery_Status);
CREATE INDEX IF NOT EXISTS idx_shipments_courier ON shipments(Courier_ID);
CREATE INDEX IF NOT EXISTS idx_shipments_hub ON shipments(Origin_Hub_ID);
CREATE INDEX IF NOT EXISTS idx_shipments_service ON shipments(Service_Type);
CREATE INDEX IF NOT EXISTS idx_events_shipment ON delivery_events(Shipment_ID,Event_DateTime);