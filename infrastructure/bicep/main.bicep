// ============================================================================
// Proaktiv Dokument Hub - Azure Container Apps Infrastructure
// ============================================================================
// Simplified single-user deployment - SQLite in container (ephemeral)
// Template files stored in Azure Blob Storage (persistent)
// ============================================================================

@description('The location for all resources')
param location string = resourceGroup().location

@description('Environment name (dev, staging, prod)')
@allowed(['dev', 'staging', 'prod'])
param environment string = 'prod'

@description('Base name for resources')
param baseName string = 'dokumenthub'

@description('Container image for backend')
param backendImage string

@description('Container image for frontend')
param frontendImage string

@description('Azure Storage connection string for blob storage')
@secure()
param azureStorageConnectionString string

@description('Application secret key for JWT/session signing')
@secure()
param secretKey string

// Legacy params - kept for backward compatibility but not used
@description('Azure Storage Account name (legacy - not used)')
param storageAccountName string = ''

@description('Azure Storage Account key (legacy - not used)')
@secure()
param storageAccountKey string = ''

@description('File share name (legacy - not used)')
param fileShareName string = ''

// ============================================================================
// Variables
// ============================================================================

var envSuffix = environment == 'prod' ? '' : '-${environment}'
var containerAppEnvName = '${baseName}-env${envSuffix}'
var backendAppName = '${baseName}-api${envSuffix}'
var frontendAppName = '${baseName}-web${envSuffix}'
var logAnalyticsName = '${baseName}-logs${envSuffix}'

// ============================================================================
// Log Analytics Workspace
// ============================================================================

resource logAnalytics 'Microsoft.OperationalInsights/workspaces@2022-10-01' = {
  name: logAnalyticsName
  location: location
  properties: {
    sku: {
      name: 'PerGB2018'
    }
    retentionInDays: 30
  }
}

// ============================================================================
// Container Apps Environment
// ============================================================================

resource containerAppEnv 'Microsoft.App/managedEnvironments@2023-05-01' = {
  name: containerAppEnvName
  location: location
  properties: {
    appLogsConfiguration: {
      destination: 'log-analytics'
      logAnalyticsConfiguration: {
        customerId: logAnalytics.properties.customerId
        sharedKey: logAnalytics.listKeys().primarySharedKey
      }
    }
  }
}

// ============================================================================
// Backend Container App (FastAPI)
// ============================================================================

resource backendApp 'Microsoft.App/containerApps@2023-05-01' = {
  name: backendAppName
  location: location
  properties: {
    managedEnvironmentId: containerAppEnv.id
    configuration: {
      ingress: {
        external: true
        targetPort: 8000
        transport: 'http'
        corsPolicy: {
          allowedOrigins: [
            'https://${frontendAppName}.${containerAppEnv.properties.defaultDomain}'
            'http://localhost:3000'
            'http://localhost:3001'
          ]
          allowedMethods: ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS']
          allowedHeaders: ['*']
          allowCredentials: true
        }
      }
      secrets: [
        {
          name: 'azure-storage-connection-string'
          value: azureStorageConnectionString
        }
        {
          name: 'secret-key'
          value: secretKey
        }
      ]
    }
    template: {
      containers: [
        {
          name: 'backend'
          image: backendImage
          resources: {
            cpu: json('0.25')
            memory: '0.5Gi'
          }
          env: [
            {
              // SQLite in container - ephemeral but simple
              // Template files are in Azure Blob Storage (persistent)
              name: 'DATABASE_URL'
              value: 'sqlite:///./app.db'
            }
            {
              name: 'AZURE_STORAGE_CONNECTION_STRING'
              secretRef: 'azure-storage-connection-string'
            }
            {
              name: 'SECRET_KEY'
              secretRef: 'secret-key'
            }
            {
              name: 'APP_ENV'
              value: environment
            }
            {
              name: 'LOG_LEVEL'
              value: environment == 'prod' ? 'WARNING' : 'INFO'
            }
            {
              name: 'DEBUG'
              value: environment == 'prod' ? 'false' : 'true'
            }
          ]
          probes: [
            {
              type: 'liveness'
              httpGet: {
                path: '/api/health'
                port: 8000
              }
              initialDelaySeconds: 15
              periodSeconds: 30
            }
            {
              type: 'readiness'
              httpGet: {
                path: '/api/health'
                port: 8000
              }
              initialDelaySeconds: 10
              periodSeconds: 10
            }
          ]
        }
      ]
      scale: {
        minReplicas: 1
        maxReplicas: 1  // Single user, no need for scaling
      }
    }
  }
}

// ============================================================================
// Frontend Container App (Next.js)
// ============================================================================

resource frontendApp 'Microsoft.App/containerApps@2023-05-01' = {
  name: frontendAppName
  location: location
  properties: {
    managedEnvironmentId: containerAppEnv.id
    configuration: {
      ingress: {
        external: true
        targetPort: 3000
        transport: 'http'
      }
    }
    template: {
      containers: [
        {
          name: 'frontend'
          image: frontendImage
          resources: {
            cpu: json('0.25')
            memory: '0.5Gi'
          }
          env: [
            {
              name: 'BACKEND_URL'
              value: 'https://${backendApp.properties.configuration.ingress.fqdn}'
            }
            {
              name: 'NODE_ENV'
              value: 'production'
            }
          ]
          probes: [
            {
              type: 'liveness'
              httpGet: {
                path: '/'
                port: 3000
              }
              initialDelaySeconds: 15
              periodSeconds: 30
            }
            {
              type: 'readiness'
              httpGet: {
                path: '/'
                port: 3000
              }
              initialDelaySeconds: 10
              periodSeconds: 10
            }
          ]
        }
      ]
      scale: {
        minReplicas: 1
        maxReplicas: 1  // Single user, no need for scaling
      }
    }
  }
}

// ============================================================================
// Outputs
// ============================================================================

output containerAppEnvironmentId string = containerAppEnv.id
output backendUrl string = 'https://${backendApp.properties.configuration.ingress.fqdn}'
output frontendUrl string = 'https://${frontendApp.properties.configuration.ingress.fqdn}'
output backendAppName string = backendApp.name
output frontendAppName string = frontendApp.name
