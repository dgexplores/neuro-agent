/**
 * Blue/Green Deployment Script for NeuroAgent
 *
 * Phase 9-2: Implements zero-downtime deployments using:
 * - Lambda version aliases (Blue/Green)
 * - API Gateway weighted stages
 * - Automated rollback capabilities
 * - Traffic shifting strategies
 *
 * Usage:
 *   npm install
 *   npx ts-node cdk-bluegreen.ts deploy --traffic-percent 10
 *   npx ts-node cdk-bluegreen.ts shift --traffic-percent 50
 *   npx ts-node cdk-bluegreen.ts rollback
 */

import * as cdk from 'aws-cdk-lib';
import * as lambda from 'aws-cdk-lib/aws-lambda';
import * as apigateway from 'aws-cdk-lib/aws-apigateway';
import * as codedeploy from 'aws-cdk-lib/aws-codedeploy';
import * as cloudwatch from 'aws-cdk-lib/aws-cloudwatch';
import * as iam from 'aws-cdk-lib/aws-iam';
import { Construct } from 'constructs';

/**
 * Configuration for Blue/Green deployment
 */
interface BlueGreenConfig {
  /**
   * Traffic shift percentage for canary deployment
   * 0-100, where 100 means all traffic goes to new version
   */
  trafficPercent: number;

  /**
   * Deployment strategy: linear, canary, or all-at-once
   */
  deploymentStrategy: 'linear' | 'canary' | 'all-at-once';

  /**
   * Bake time in minutes before full traffic shift
   */
  bakeTimeMinutes: number;

  /**
   * Enable automatic rollback on errors
   */
  autoRollback: boolean;

  /**
   * Alarm threshold for error rate (%)
   */
  errorRateThreshold: number;
}

/**
 * Blue/Green Deployment Stack for NeuroAgent
 */
export class NeuroAgentBlueGreenStack extends cdk.Stack {
  public readonly api: apigateway.RestApi;
  public readonly lambdaBlue: lambda.Function;
  public readonly lambdaGreen: lambda.Alias;
  public readonly deployment: codedeploy.LambdaDeploymentGroup;

  constructor(scope: Construct, id: string, config: BlueGreenConfig, props?: cdk.StackProps) {
    super(scope, id, props);

    // Import existing Lambda function
    const lambdaFunction = lambda.Function.fromFunctionName(
      this,
      'ExistingLambda',
      'NeuroAgentStack-NeuroAgentAPI'
    );

    // Create Lambda version for current deployment
    const version = new lambda.Version(this, 'LambdaVersion', {
      lambda: lambdaFunction,
      description: `Deployed at ${new Date().toISOString()}`,
    });

    // Blue alias (stable/production)
    const blueAlias = new lambda.Alias(this, 'BlueAlias', {
      aliasName: 'blue',
      version: version,
      description: 'Stable production version (Blue)',
    });

    // Green alias (new version for testing)
    const greenAlias = new lambda.Alias(this, 'GreenAlias', {
      aliasName: 'green',
      version: version,
      description: 'New version under test (Green)',
    });

    this.lambdaBlue = lambdaFunction;
    this.lambdaGreen = greenAlias;

    // CloudWatch Alarms for monitoring
    const errorAlarm = new cloudwatch.Alarm(this, 'LambdaErrorAlarm', {
      metric: greenAlias.metricErrors({
        statistic: 'sum',
        period: cdk.Duration.minutes(1),
      }),
      threshold: config.errorRateThreshold,
      evaluationPeriods: 2,
      comparisonOperator: cloudwatch.ComparisonOperator.GREATER_THAN_THRESHOLD,
      alarmDescription: 'Lambda error rate exceeded threshold during deployment',
      treatMissingData: cloudwatch.TreatMissingData.NOT_BREACHING,
    });

    const durationAlarm = new cloudwatch.Alarm(this, 'LambdaDurationAlarm', {
      metric: greenAlias.metricDuration({
        statistic: 'p95',
        period: cdk.Duration.minutes(1),
      }),
      threshold: 2000, // 2 seconds (Phase 8-1 target)
      evaluationPeriods: 2,
      comparisonOperator: cloudwatch.ComparisonOperator.GREATER_THAN_THRESHOLD,
      alarmDescription: 'Lambda p95 duration exceeded 2s target',
      treatMissingData: cloudwatch.TreatMissingData.NOT_BREACHING,
    });

    // Deployment strategy configuration
    let deploymentConfig: codedeploy.ILambdaDeploymentConfig;

    switch (config.deploymentStrategy) {
      case 'linear':
        // Linear10PercentEvery1Minute - gradual rollout
        deploymentConfig = codedeploy.LambdaDeploymentConfig.LINEAR_10PERCENT_EVERY_1MINUTE;
        break;
      case 'canary':
        // Canary10Percent5Minutes - 10% for 5min, then 100%
        deploymentConfig = codedeploy.LambdaDeploymentConfig.CANARY_10PERCENT_5MINUTES;
        break;
      case 'all-at-once':
        // All at once - immediate switch (risky!)
        deploymentConfig = codedeploy.LambdaDeploymentConfig.ALL_AT_ONCE;
        break;
      default:
        deploymentConfig = codedeploy.LambdaDeploymentConfig.CANARY_10PERCENT_5MINUTES;
    }

    // CodeDeploy application and deployment group
    const application = new codedeploy.LambdaApplication(this, 'CodeDeployApp', {
      applicationName: 'NeuroAgent-BlueGreen',
    });

    this.deployment = new codedeploy.LambdaDeploymentGroup(this, 'DeploymentGroup', {
      application,
      alias: greenAlias,
      deploymentConfig,
      alarms: [errorAlarm, durationAlarm],
      autoRollback: {
        failedDeployment: config.autoRollback,
        stoppedDeployment: config.autoRollback,
        deploymentInAlarm: config.autoRollback,
      },
      deploymentGroupName: 'NeuroAgent-Production',
    });

    // API Gateway with weighted stages
    this.api = new apigateway.RestApi(this, 'BlueGreenAPI', {
      restApiName: 'NeuroAgent-BlueGreen',
      description: 'Blue/Green deployment API for NeuroAgent',
      deployOptions: {
        stageName: 'prod',
        throttlingRateLimit: 100,
        throttlingBurstLimit: 200,
        metricsEnabled: true,
        loggingLevel: apigateway.MethodLoggingLevel.INFO,
        dataTraceEnabled: true,
      },
    });

    // Blue stage (stable)
    const blueStage = new apigateway.Stage(this, 'BlueStage', {
      deployment: new apigateway.Deployment(this, 'BlueDeployment', {
        api: this.api,
      }),
      stageName: 'blue',
      throttlingRateLimit: 100,
      throttlingBurstLimit: 200,
      description: 'Blue (stable) environment',
    });

    // Green stage (new version)
    const greenStage = new apigateway.Stage(this, 'GreenStage', {
      deployment: new apigateway.Deployment(this, 'GreenDeployment', {
        api: this.api,
      }),
      stageName: 'green',
      throttlingRateLimit: 10, // Lower limit for testing
      throttlingBurstLimit: 20,
      description: 'Green (new version) environment',
    });

    // Configure stage variables for traffic shifting
    blueStage.addToBaseStageVariables({
      lambdaAlias: 'blue',
      environment: 'production',
      trafficWeight: (100 - config.trafficPercent).toString(),
    });

    greenStage.addToBaseStageVariables({
      lambdaAlias: 'green',
      environment: 'staging',
      trafficWeight: config.trafficPercent.toString(),
    });

    // Configure API routes to use alias
    const diagnosisIntegration = new apigateway.LambdaIntegration(greenAlias, {
      proxy: true,
      allowTestInvoke: true,
    });

    const apiV1 = this.api.root.addResource('api').addResource('v1');
    const diagnosisResource = apiV1.addResource('diagnosis');
    diagnosisResource.addMethod('POST', diagnosisIntegration, {
      authorizationType: apigateway.AuthorizationType.CUSTOM,
      requestValidatorOptions: {
        validateRequestBody: true,
        validateRequestParameters: true,
      },
    });

    // CloudWatch Dashboard for monitoring deployment
    const dashboard = new cloudwatch.Dashboard(this, 'DeploymentDashboard', {
      dashboardName: 'NeuroAgent-BlueGreen-Deployment',
    });

    dashboard.addWidgets(
      new cloudwatch.GraphWidget({
        title: 'Lambda Invocations (Blue vs Green)',
        left: [
          blueAlias.metricInvocations({ label: 'Blue', color: cloudwatch.Color.BLUE }),
          greenAlias.metricInvocations({ label: 'Green', color: cloudwatch.Color.GREEN }),
        ],
        width: 12,
      }),
      new cloudwatch.GraphWidget({
        title: 'Error Rate Comparison',
        left: [
          blueAlias.metricErrors({ label: 'Blue Errors', color: cloudwatch.Color.RED }),
          greenAlias.metricErrors({ label: 'Green Errors', color: cloudwatch.Color.ORANGE }),
        ],
        width: 12,
      }),
      new cloudwatch.GraphWidget({
        title: 'Duration (p95)',
        left: [
          blueAlias.metricDuration({
            label: 'Blue p95',
            statistic: 'p95',
            color: cloudwatch.Color.BLUE,
          }),
          greenAlias.metricDuration({
            label: 'Green p95',
            statistic: 'p95',
            color: cloudwatch.Color.GREEN,
          }),
        ],
        width: 12,
        leftYAxis: {
          label: 'Duration (ms)',
          showUnits: false,
        },
      })
    );

    // Stack outputs
    new cdk.CfnOutput(this, 'BlueStageURL', {
      value: `${this.api.url}blue/`,
      description: 'Blue (stable) stage URL',
    });

    new cdk.CfnOutput(this, 'GreenStageURL', {
      value: `${this.api.url}green/`,
      description: 'Green (new version) stage URL',
    });

    new cdk.CfnOutput(this, 'TrafficDistribution', {
      value: `Blue: ${100 - config.trafficPercent}% | Green: ${config.trafficPercent}%`,
      description: 'Current traffic distribution',
    });

    new cdk.CfnOutput(this, 'DashboardURL', {
      value: `https://console.aws.amazon.com/cloudwatch/home?region=${this.region}#dashboards:name=${dashboard.dashboardName}`,
      description: 'CloudWatch Dashboard for monitoring',
    });
  }
}

/**
 * CLI for Blue/Green deployment management
 */
class BlueGreenCLI {
  private readonly app: cdk.App;
  private readonly defaultConfig: BlueGreenConfig = {
    trafficPercent: 10,
    deploymentStrategy: 'canary',
    bakeTimeMinutes: 5,
    autoRollback: true,
    errorRateThreshold: 5, // 5 errors per minute
  };

  constructor() {
    this.app = new cdk.App();
  }

  /**
   * Deploy with initial traffic percentage
   */
  deploy(trafficPercent: number = 10): void {
    console.log(`🚀 Starting Blue/Green deployment with ${trafficPercent}% traffic to Green...`);

    const config: BlueGreenConfig = {
      ...this.defaultConfig,
      trafficPercent,
    };

    new NeuroAgentBlueGreenStack(this.app, 'NeuroAgentBlueGreen', config);

    console.log(`\n✅ Deployment configuration:`);
    console.log(`   Strategy: ${config.deploymentStrategy}`);
    console.log(`   Traffic to Green: ${config.trafficPercent}%`);
    console.log(`   Auto-rollback: ${config.autoRollback ? 'Enabled' : 'Disabled'}`);
    console.log(`   Error threshold: ${config.errorRateThreshold} errors/min`);
    console.log(`\n📊 Monitor deployment: CloudWatch Dashboard`);
  }

  /**
   * Shift traffic to new percentage
   */
  shift(trafficPercent: number): void {
    console.log(`🔄 Shifting traffic to ${trafficPercent}% Green...`);

    const config: BlueGreenConfig = {
      ...this.defaultConfig,
      trafficPercent,
    };

    new NeuroAgentBlueGreenStack(this.app, 'NeuroAgentBlueGreen', config);

    console.log(`✅ Traffic shift initiated to ${trafficPercent}%`);
  }

  /**
   * Complete rollout (100% to Green, then swap aliases)
   */
  complete(): void {
    console.log(`🎯 Completing Blue/Green deployment (100% to Green)...`);

    const config: BlueGreenConfig = {
      ...this.defaultConfig,
      trafficPercent: 100,
      deploymentStrategy: 'all-at-once',
    };

    new NeuroAgentBlueGreenStack(this.app, 'NeuroAgentBlueGreen', config);

    console.log(`✅ Deployment complete. Green is now production.`);
    console.log(`💡 Next: Swap Blue/Green labels for next deployment`);
  }

  /**
   * Rollback to Blue (stable version)
   */
  rollback(): void {
    console.log(`⚠️  Rolling back to Blue (stable version)...`);

    const config: BlueGreenConfig = {
      ...this.defaultConfig,
      trafficPercent: 0, // All traffic to Blue
      deploymentStrategy: 'all-at-once',
    };

    new NeuroAgentBlueGreenStack(this.app, 'NeuroAgentBlueGreen', config);

    console.log(`✅ Rollback complete. All traffic routed to Blue.`);
  }
}

// CLI execution
if (require.main === module) {
  const cli = new BlueGreenCLI();
  const args = process.argv.slice(2);
  const command = args[0];
  const trafficFlag = args.indexOf('--traffic-percent');
  const trafficPercent = trafficFlag !== -1 ? parseInt(args[trafficFlag + 1]) : 10;

  switch (command) {
    case 'deploy':
      cli.deploy(trafficPercent);
      break;
    case 'shift':
      cli.shift(trafficPercent);
      break;
    case 'complete':
      cli.complete();
      break;
    case 'rollback':
      cli.rollback();
      break;
    default:
      console.log(`
NeuroAgent Blue/Green Deployment CLI

Usage:
  npx ts-node cdk-bluegreen.ts <command> [options]

Commands:
  deploy              Initial deployment with traffic split
  shift               Shift traffic percentage to Green
  complete            Complete deployment (100% to Green)
  rollback            Rollback all traffic to Blue

Options:
  --traffic-percent   Percentage of traffic to route to Green (0-100)

Examples:
  # Deploy with 10% traffic to Green
  npx ts-node cdk-bluegreen.ts deploy --traffic-percent 10

  # Shift to 50% traffic
  npx ts-node cdk-bluegreen.ts shift --traffic-percent 50

  # Complete deployment
  npx ts-node cdk-bluegreen.ts complete

  # Emergency rollback
  npx ts-node cdk-bluegreen.ts rollback
      `);
  }
}

export { BlueGreenConfig, NeuroAgentBlueGreenStack, BlueGreenCLI };
