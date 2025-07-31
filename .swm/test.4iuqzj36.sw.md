---
title: Test
---
# Introduction

This document explains the setup and configuration choices made for the Jest testing environment in the project. We will cover:

1. How TypeScript integration is handled in Jest.
2. How ECMAScript module (ESM) dependencies are managed during transformation.
3. How <SwmPath>[test](/test)</SwmPath> file patterns and module path mappings are configured.
4. How coverage collection and reporting are controlled, especially in CI environments.

# TypeScript integration in Jest

The configuration uses <SwmToken path="/jest.config.js" pos="1:13:15" line-data="const { pathsToModuleNameMapper } = require(&#39;ts-jest&#39;);">`ts-jest`</SwmToken> with specific options to handle TypeScript files. It sets <SwmToken path="/jest.config.js" pos="6:1:1" line-data="	isolatedModules: true,">`isolatedModules`</SwmToken> to true to speed up compilation by transpiling files independently, and disables declaration file generation to avoid unnecessary output during tests. Source maps are enabled to improve debugging of <SwmPath>[test](/test)</SwmPath> failures by mapping back to the original TypeScript source.

<SwmSnippet path="/jest.config.js" line="1">

---

This setup is defined in <SwmPath>[jest.config.js](/jest.config.js)</SwmPath> and ensures that TypeScript files are properly compiled and tested without extra overhead.

```
const { pathsToModuleNameMapper } = require('ts-jest');
const { compilerOptions } = require('get-tsconfig').getTsconfig().config;

/** @type {import('ts-jest').TsJestGlobalOptions} */
const tsJestOptions = {
	isolatedModules: true,
	tsconfig: {
		...compilerOptions,
		declaration: false,
		sourceMap: true,
	},
};
```

---

</SwmSnippet>

# handling ESM dependencies in Jest

Some dependencies are published as ECMAScript modules, which Jest cannot transform by default. To address this, a list of such ESM dependencies is maintained. These dependencies are explicitly transformed using <SwmToken path="/jest.config.js" pos="36:2:4" line-data="			&#39;babel-jest&#39;,">`babel-jest`</SwmToken> with presets and plugins that support ESM features like `import.meta`.

<SwmSnippet path="/jest.config.js" line="14">

---

This approach allows Jest to run tests that depend on these modules without errors related to unsupported syntax.

```
const isCoverageEnabled = process.env.COVERAGE_ENABLED === 'true';

const esmDependencies = [
	'pdfjs-dist',
	'openid-client',
	'oauth4webapi',
	'jose',
	// Add other ESM dependencies that need to be transformed here
];
```

---

</SwmSnippet>

# <SwmPath>[test](/test)</SwmPath> matching, transformation, and module resolution

The Jest config specifies which files to consider as tests using regex patterns that match `.test` or `.spec` files with <SwmToken path="/jest.config.js" pos="44:28:29" line-data="	// This resolve the path mappings from the tsconfig relative to each jest.config.js">`.js`</SwmToken> or `.ts` extensions. It excludes <SwmToken path="/jest.config.js" pos="17:4:4" line-data="	&#39;pdfjs-dist&#39;,">`dist`</SwmToken> and <SwmToken path="/jest.config.js" pos="25:7:7" line-data="const esmDependenciesRegex = `node_modules/(${esmDependenciesPattern})/.+\\.m?js$`;">`node_modules`</SwmToken> folders to avoid unnecessary processing.

Transformations are set up to use <SwmToken path="/jest.config.js" pos="1:13:15" line-data="const { pathsToModuleNameMapper } = require(&#39;ts-jest&#39;);">`ts-jest`</SwmToken> for TypeScript files and <SwmToken path="/jest.config.js" pos="36:2:4" line-data="			&#39;babel-jest&#39;,">`babel-jest`</SwmToken> for the ESM dependencies identified earlier. The <SwmToken path="/jest.config.js" pos="43:1:1" line-data="	transformIgnorePatterns: [`/node_modules/(?!${esmDependenciesPattern})/`],">`transformIgnorePatterns`</SwmToken> option excludes all <SwmToken path="/jest.config.js" pos="25:7:7" line-data="const esmDependenciesRegex = `node_modules/(${esmDependenciesPattern})/.+\\.m?js$`;">`node_modules`</SwmToken> except the ESM dependencies, ensuring only those are transformed.

Module path aliases from the TypeScript configuration are mapped into Jest using <SwmToken path="/jest.config.js" pos="1:4:4" line-data="const { pathsToModuleNameMapper } = require(&#39;ts-jest&#39;);">`pathsToModuleNameMapper`</SwmToken>. This keeps import paths consistent between the application code and tests.

<SwmSnippet path="/jest.config.js" line="24">

---

Additional setup includes enabling verbose output, setting the <SwmPath>[test](/test)</SwmPath> environment to Node.js, and adding a custom matcher extension via <SwmToken path="/jest.config.js" pos="50:6:10" line-data="	setupFilesAfterEnv: [&#39;jest-expect-message&#39;],">`jest-expect-message`</SwmToken>.

```
const esmDependenciesPattern = esmDependencies.join('|');
const esmDependenciesRegex = `node_modules/(${esmDependenciesPattern})/.+\\.m?js$`;

/** @type {import('jest').Config} */
const config = {
	verbose: true,
	testEnvironment: 'node',
	testRegex: '\\.(test|spec)\\.(js|ts)$',
	testPathIgnorePatterns: ['/dist/', '/node_modules/'],
	transform: {
		'^.+\\.ts$': ['ts-jest', tsJestOptions],
		[esmDependenciesRegex]: [
			'babel-jest',
			{
				presets: ['@babel/preset-env'],
				plugins: ['babel-plugin-transform-import-meta'],
			},
		],
	},
	transformIgnorePatterns: [`/node_modules/(?!${esmDependenciesPattern})/`],
	// This resolve the path mappings from the tsconfig relative to each jest.config.js
	moduleNameMapper: compilerOptions?.paths
		? pathsToModuleNameMapper(compilerOptions.paths, {
				prefix: `<rootDir>${compilerOptions.baseUrl ? `/${compilerOptions.baseUrl.replace(/^\.\//, '')}` : ''}`,
			})
		: {},
	setupFilesAfterEnv: ['jest-expect-message'],
	collectCoverage: isCoverageEnabled,
	coverageReporters: ['text-summary', 'lcov', 'html-spa'],
	workerIdleMemoryLimit: '1MB',
};
```

---

</SwmSnippet>

# coverage collection and CI-specific settings

Coverage collection is controlled by an environment variable <SwmToken path="/jest.config.js" pos="14:10:10" line-data="const isCoverageEnabled = process.env.COVERAGE_ENABLED === &#39;true&#39;;">`COVERAGE_ENABLED`</SwmToken>. When enabled, coverage reports are generated in multiple formats including text summary, lcov, and an HTML single-page app.

In continuous integration environments (detected via <SwmToken path="/jest.config.js" pos="56:7:7" line-data="if (process.env.CI === &#39;true&#39;) {">`CI`</SwmToken> environment variable), coverage collection is restricted to source files only. The reporters are adjusted to include <SwmToken path="/jest.config.js" pos="58:14:16" line-data="	config.reporters = [&#39;default&#39;, &#39;jest-junit&#39;];">`jest-junit`</SwmToken> for <SwmPath>[test](/test)</SwmPath> results and <SwmToken path="/jest.config.js" pos="59:9:9" line-data="	config.coverageReporters = [&#39;cobertura&#39;];">`cobertura`</SwmToken> for coverage, formats commonly used by CI tools.

<SwmSnippet path="/jest.config.js" line="56">

---

This conditional setup ensures that local development and CI environments have appropriate coverage and reporting configurations without manual changes.

```
if (process.env.CI === 'true') {
	config.collectCoverageFrom = ['src/**/*.ts'];
	config.reporters = ['default', 'jest-junit'];
	config.coverageReporters = ['cobertura'];
}

module.exports = config;
```

---

</SwmSnippet>

<SwmMeta version="3.0.0" repo-id="Z2l0aHViJTNBJTNBbjhuJTNBJTNBdXByYXRpay1jdA==" repo-name="n8n"><sup>Powered by [Swimm](https://app.swimm.io/)</sup></SwmMeta>
