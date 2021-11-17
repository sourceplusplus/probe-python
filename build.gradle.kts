plugins {
    id("ru.vyarus.use-python") version "2.3.0"
    id("com.avast.gradle.docker-compose")
}

python {
    pip("apache-skywalking:0.7.0")
    pip("vertx-eventbus-client:1.0.0")    
}

tasks {
    register<Exec>("buildDist") {
        commandLine("sh", "-c", "python setup.py sdist")
    }

    register<Copy>("updateDockerFiles") {
        dependsOn("buildDist")
        from("dist/")
        into("e2e/")
    }

    register("assembleUp") {
        dependsOn("updateDockerFiles", "composeUp")
    }
    getByName("composeUp").mustRunAfter("updateDockerFiles")
}

dockerCompose {
    dockerComposeWorkingDirectory.set(File("./e2e"))
    removeVolumes.set(true)
    waitForTcpPorts.set(false)
}
