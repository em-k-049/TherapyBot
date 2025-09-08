#!/bin/bash

echo "Starting TherapyBot Monitoring Stack..."

# Start monitoring services
docker-compose -f docker-compose.monitoring.yml up -d

echo "Waiting for services to start..."
sleep 30

echo "Monitoring stack started successfully!"
echo ""
echo "Access URLs:"
echo "- Elasticsearch: http://localhost:9200"
echo "- Kibana: http://localhost:5601"
echo "- Prometheus: http://localhost:9090"
echo "- Grafana: http://localhost:3001 (admin/admin123)"
echo "- TherapyBot Metrics: http://localhost:8000/metrics"
echo ""
echo "To view logs in Kibana:"
echo "1. Go to http://localhost:5601"
echo "2. Create index pattern: therapybot-*"
echo "3. Use @timestamp as time field"
echo ""
echo "To stop monitoring stack:"
echo "docker-compose -f docker-compose.monitoring.yml down"