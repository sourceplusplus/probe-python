plugins {
    id("ru.vyarus.use-python") version "3.0.0"
    id("com.avast.gradle.docker-compose")
}

python {
    pip("apache-skywalking:1.0.0")
    pip("vertx-eventbus-client:1.0.0")    
}

tasks {
    register<Exec>("buildDist") {
        executable = "python3"
        args("setup.py", "sdist")
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
    waitForTcpPorts.set(false)
}
