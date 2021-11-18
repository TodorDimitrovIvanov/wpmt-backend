def app

pipeline{
	agent{
		label 'jenkins-slave-agent-01'
	}
	environment{ 
	dockerRegistry = "docker-registry.wpmt.org"
	dockerRepo = "wpmt-client-backend"
	dockerCredentials = credentials('docker-registry')
	}
	// Here we declare that our Jenkins Agent will be 
	// using Python 3.9.2 image from the public Docker registry
	stages{
		// Here we declare the steps of the Pipeline
		stage ('Checkout from GitHub'){
			agent{
				label 'jenkins-slave-agent-01'
			}
			steps{
				checkout scm
			}
		}
		stage('Build Docker image'){
			agent{
				label 'jenkins-slave-agent-01'
			}
			steps{
				script{
					def imageVersion = readFile('VERSION')
					sh """
						docker build -t dev/$dockerRepo:$imageVersion -f Dockerfile .
					"""
				}
			}
		}	
		stage('Push Docker image'){
			agent{
				label 'jenkins-slave-agent-01'
			}
			steps{
				script{
					def imageVersion = readFile('VERSION')
					sh """
						docker login $dockerRegistry -u $dockerCredentials_USR -p $dockerCredentials_PSW
						docker tag dev/$dockerRepo:$imageVersion $dockerRegistry/$dockerCredentials_USR/$dockerRepo:$imageVersion
						docker push $dockerRegistry/$dockerCredentials_USR/$dockerRepo:$imageVersion 
					"""
				}
			}
		}
		stage('Provision image'){
			agent{
				label 'jenkins-slave-agent-01'
			}
			steps{
				script{
					// TODO: Add Helm intergration
					echo(message: "Helm integration not yet completed")
				}
			}
		}
	}
}
