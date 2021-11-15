plugins {
    id("ru.vyarus.use-python") version "2.3.0"
}

python {
    pip("apache-skywalking:0.7.0")
    pip("vertx-eventbus-client:1.0.0")    
}
