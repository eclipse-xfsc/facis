"use strict";
/**
 * Patched version of node-red-contrib-rdkafka/rdkafka/rdkafka.js
 * Adds SSL/TLS support to kafka-broker config node for mTLS connections.
 *
 * Additional broker config properties (optional):
 *   securityProtocol  - "ssl" to enable TLS (default: plaintext)
 *   sslCaLocation     - path to CA certificate file
 *   sslCertLocation   - path to client certificate file
 *   sslKeyLocation    - path to client key file
 */
module.exports = function(RED) {
    var Kafka = require('node-rdkafka');
    var util = require("util");

    function KafkaBrokerNode(n) {
        RED.nodes.createNode(this, n);
        this.broker = n.broker;
        this.clientid = n.clientid;
        // SSL/TLS properties (FACIS patch)
        this.securityProtocol = n.securityProtocol || "";
        this.sslCaLocation = n.sslCaLocation || "";
        this.sslCertLocation = n.sslCertLocation || "";
        this.sslKeyLocation = n.sslKeyLocation || "";
    }

    /**
     * Build base librdkafka config from broker node, including SSL if configured.
     */
    KafkaBrokerNode.prototype.getBaseConfig = function() {
        var config = {
            'client.id': this.clientid || 'node-red',
            'metadata.broker.list': this.broker,
            'socket.keepalive.enable': true,
            'api.version.request': true
        };
        if (this.securityProtocol === 'ssl') {
            config['security.protocol'] = 'ssl';
            if (this.sslCaLocation)   config['ssl.ca.location'] = this.sslCaLocation;
            if (this.sslCertLocation) config['ssl.certificate.location'] = this.sslCertLocation;
            if (this.sslKeyLocation)  config['ssl.key.location'] = this.sslKeyLocation;
            util.log('[rdkafka] SSL enabled for broker ' + this.broker);
        }
        return config;
    };

    RED.nodes.registerType("kafka-broker", KafkaBrokerNode, {});

    function RdKafkaInNode(n) {
        RED.nodes.createNode(this, n);
        this.topic = n.topic;
        this.broker = n.broker;
        this.cgroup = n.cgroup;
        this.autocommit = n.autocommit;
        this.brokerConfig = RED.nodes.getNode(this.broker);
        var node = this;
        var consumer;
        if (node.brokerConfig !== undefined) {
            node.status({ fill: "red", shape: "ring", text: "disconnected" });
            if (node.topic !== undefined) {
                try {
                    var consumerConfig = Object.assign(node.brokerConfig.getBaseConfig(), {
                        'group.id': node.cgroup,
                        'enable.auto.commit': node.autocommit,
                        'queue.buffering.max.ms': 1,
                        'fetch.min.bytes': 1,
                        'fetch.wait.max.ms': 1,
                        'fetch.error.backoff.ms': 100
                    });
                    consumer = new Kafka.KafkaConsumer(consumerConfig, {});
                    consumer.connect();
                    consumer
                        .on('ready', function() {
                            node.status({ fill: "green", shape: "dot", text: "connected" });
                            consumer.subscribe([node.topic]);
                            consumer.consume();
                            util.log('[rdkafka] Created consumer subscription on topic = ' + node.topic);
                        })
                        .on('data', function(data) {
                            var msg = {
                                topic: data.topic,
                                offset: data.offset,
                                partition: data.partition,
                                size: data.size
                            };
                            msg.payload = data.value ? data.value.toString() : "";
                            if (data.key) msg.key = data.key.toString();
                            try { node.send(msg); } catch(e) {
                                util.log('[rdkafka] error sending node message: ' + e);
                            }
                        })
                        .on('error', function(err) {
                            console.error('[rdkafka] Error in consumer: ' + err);
                        });
                } catch(e) {
                    util.log('[rdkafka] Error creating consumer: ' + e);
                }
            } else {
                node.error('missing input topic');
            }
        } else {
            node.error("missing broker configuration");
        }
        node.on('close', function() {
            node.status({ fill: "red", shape: "ring", text: "disconnected" });
            try { consumer.unsubscribe([node.topic]); consumer.disconnect(); } catch(e) {}
        });
    }
    RED.nodes.registerType("rdkafka in", RdKafkaInNode);

    function RdKafkaOutNode(n) {
        RED.nodes.createNode(this, n);
        this.topic = n.topic;
        this.broker = n.broker;
        this.key = n.key;
        this.partition = Number(n.partition);
        this.brokerConfig = RED.nodes.getNode(this.broker);
        var node = this;
        var producer;

        if (node.brokerConfig !== undefined) {
            node.status({ fill: "red", shape: "ring", text: "disconnected" });

            try {
                var producerConfig = Object.assign(node.brokerConfig.getBaseConfig(), {
                    'retry.backoff.ms': 200,
                    'message.send.max.retries': 15,
                    'queue.buffering.max.messages': 100000,
                    'queue.buffering.max.ms': 10,
                    'batch.num.messages': 1000000
                });
                producer = new Kafka.Producer(producerConfig);
                producer.connect();

                producer.on('ready', function() {
                    util.log('[rdkafka] Producer ready for broker ' + node.brokerConfig.broker);
                    node.status({ fill: "green", shape: "dot", text: "connected" });
                });

                producer.on('error', function(err) {
                    console.error('[rdkafka] Producer error: ' + err);
                    node.status({ fill: "red", shape: "ring", text: "error" });
                });

            } catch(e) {
                console.log('[rdkafka] Error creating producer: ' + e);
            }

            this.on("input", function(msg) {
                var partition, key, topic, value, timestamp;

                partition = (this.partition >= 0) ? this.partition :
                            (msg.partition >= 0) ? Number(msg.partition) : -1;

                key = this.key || msg.key || null;

                topic = (this.topic === "" && msg.topic !== "") ? msg.topic : this.topic;

                value = (typeof msg.payload === 'object') ?
                    JSON.stringify(msg.payload) : msg.payload.toString();

                if ((new Date(msg.timestamp)).getTime() > 0) {
                    timestamp = msg.timestamp;
                }

                if (msg === null || topic === "") {
                    util.log("[rdkafka] ignored NULL message or NULL topic");
                } else {
                    producer.produce(topic, partition, Buffer.from(value), key, timestamp);
                }
            });
        } else {
            this.error("[rdkafka] missing broker configuration");
        }
        this.on('close', function() {
            node.status({ fill: "red", shape: "ring", text: "disconnected" });
            try { producer.disconnect(); } catch(e) {}
        });
    }
    RED.nodes.registerType("rdkafka out", RdKafkaOutNode);
};
