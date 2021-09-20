
pipeline{
    // Here we declare that our Jenkins Agent will be 
    // using Python 3.9.2 image from the public Docker registry
    agent { jenkins-slave-agent-01 { image 'python:3.9.2'}}
    stages{
        // Here we deckare the steps of the Pipeline
        stage ('build'){
            steps{
                sh 'pip install -r requirements.txt'
            }
        }
    }
}