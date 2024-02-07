![Versatile Data Kit](./support/images/versatile-data-kit.svg#gh-light-mode-only)
![Versatile Data Kit](./support/images/versatile-data-kit.svg#gh-dark-mode-only)

<p align="center">
    <a href="https://github.com/vmware/versatile-data-kit/pulse" alt="Activity">
        <img src="https://img.shields.io/github/commit-activity/m/vmware/versatile-data-kit" /></a>
    <a href="https://github.com/vmware/versatile-data-kit/contributors" alt="Last Activity">
        <img src="https://img.shields.io/github/last-commit/vmware/versatile-data-kit" alt="Last Activity"></a>
    <a href="https://pypistats.org/packages/vdk-core" alt="Monthly Downloads">
        <img src="https://img.shields.io/pypi/dm/vdk-core.svg" alt="monthly download count for vdk-core"></a>
    <a href="https://github.com/vmware/versatile-data-kit/blob/main/LICENSE" alt="License">
        <img src="https://img.shields.io/github/license/vmware/versatile-data-kit" alt="license"></a>
    <a href="https://github.com/pre-commit/pre-commit">
        <img src="https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white" alt="pre-commit"></a>
    <a href="https://github.com/vmware/versatile-data-kit">
        <img src="https://gitlab.com/vmware-analytics/versatile-data-kit/badges/main/pipeline.svg" alt="build status"></a>
    <a href="https://twitter.com/intent/tweet?text=Wow: @VDKProject">
        <img src="https://img.shields.io/twitter/url?style=social&url=https%3A%2F%2Ftwitter.com%2FVDKProject" alt="twitter"/></a>
     <a href="https://www.youtube.com/channel/UCasf2Q7X8nF7S4VEmcTHJ0Q">
        <img alt="YouTube Channel Subscribers" src="https://img.shields.io/youtube/channel/subscribers/UCasf2Q7X8nF7S4VEmcTHJ0Q?style=social"></a>
</p>
<!-- TODO: code coverage -->

---

<!-- Added the line here to have some mental space between the icons, as no one in the interviews saw the first sentence -->
<p align="center">
  <span> One framework to🧑‍💻 Develop </span> <span> ▶️ Deploy </span> <span>and 📊 Operate </span> <br>
   <span>data workflows with Python and SQL<span>
</p>

---

<div align="left">
    <span>🎯 Write shorter, more readable code. </span><br>
</div>
<div align="left">
    <span>🔄 Ready-to-use data ETL/ELT patterns. </span><br>
</div>
<div align="left">
    <span>🧩 Lego-like extensibility. </span><br>
</div>
<br>
<div align="left">
    <span>🚀 Single click deployment. </span><br>
</div>
<div align="left">
    <span>🛠 Operate and monitor. ️</span><br>
</div>

---

<p id="intro" align="center">
    <a href="#intro"><img src="https://img.shields.io/badge/VDK%20SDK-blue" alt="Intro to VDK SDK"></a>
    <a href="#ingestion"><img src="https://img.shields.io/badge/Data%20Ingestion-lightblue" alt="Ingestion"></a>
    <a href="#transformation"><img src="https://img.shields.io/badge/Data%20Transformation-lightblue" alt="Transformation"></a>
    <a href="#deployment"><img src="https://img.shields.io/badge/Data%20Job%20Deployment-lightblue" alt="Job Deployment"></a>
    <a href="#operations"><img src="https://img.shields.io/badge/Data%20Job%20Operations-lightblue" alt="Job Operations"></a>
    <a href="#plugins"><img src="https://img.shields.io/badge/Lego%20like%20Extensibility-lightblue" alt="Extensibility"></a>
    <a href="#contributing"><img src="https://img.shields.io/badge/Support%20and%20Contributing-lightblue" alt="Support and Contributing"></a>
</p>
<h1>Introduction to the VDK SDK</h1>

<table width="100%" >
  <tr>
    <td width="50%" >
        <ul>
          <li>Framework to simplify data ingestion and data processing.</li>
          <li>Write any code using Python or SQL.</li>
          <li>A toolset enabling you to run data jobs.</li>
        </ul>
        <hr>
        <p><b>Get started with VDK SDK:</b></p>
        <span>&#10145; <a href="https://github.com/vmware/versatile-data-kit/wiki/Quickstart-VDK">Install Quickstart VDK</a>. Only requirement is Python 3.7+.</span><br>
        <pre><code class="bash">pip install quickstart-vdk
vdk --help</code></pre>
        <span>&#10145; Develop your <a href="https://github.com/vmware/versatile-data-kit/wiki/First-Data-Job">First Data Job</a> if you are impatient to start quickly.</span><br>
    </td>
    <td width="50%" >
        <video controls loop autoplay muted preload="metadata" src="https://github.com/vmware/versatile-data-kit/assets/2536458/1e768ddb-c622-45e2-bfd9-20dd2ae9c1dd" aria-label="30 seconds video tutorial of getting started and quickstart-vdk installation"></video>
        <!-- link to the video above https://www.canva.com/design/DAFqSRgP3xs/Tp5rVRywkwUQdUEsmWCcfw/edit?utm_content=DAFqSRgP3xs -->
    </td>
  </tr>
</table>







<br/><br/>
<p id="ingestion" align="center">
    <a href="#intro"><img src="https://img.shields.io/badge/VDK%20SDK-lightblue" alt="Intro to VDK SDK"></a>
    <a href="#ingestion"><img src="https://img.shields.io/badge/Data%20Ingestion-blue" alt="Ingestion"></a>
    <a href="#transformation"><img src="https://img.shields.io/badge/Data%20Transformation-lightblue" alt="Transformation"></a>
    <a href="#deployment"><img src="https://img.shields.io/badge/Data%20Job%20Deployment-lightblue" alt="Job Deployment"></a>
    <a href="#operations"><img src="https://img.shields.io/badge/Data%20Job%20Operations-lightblue" alt="Job Operations"></a>
    <a href="#plugins"><img src="https://img.shields.io/badge/Lego%20like%20Extensibility-lightblue" alt="Extensibility"></a>
    <a href="#contributing"><img src="https://img.shields.io/badge/Support%20and%20Contributing-lightblue" alt="Support and Contributing"></a>
</p>
<h1>Data Ingestion</h1>

<table width="100%" >
  <tr>
    <td width="50%" >
        <ul>
          <li>Extract data from various sources (HTTP APIs, Databases, CSV, etc.).</li>
          <li>Ensure data fidelity with minimal transformations.</li>
          <li>Load data to your preferred destination (database, cloud storage).</li>
        </ul>
        <hr>
        <p><b>Ingestion examples:</b></p>
        <span>&#10145;  <a href="https://github.com/vmware/versatile-data-kit/wiki/Ingesting-data-from-REST-API-into-Database">Ingesting data from REST API into Database</a> </span><br>
        <span>&#10145;  <a href="https://github.com/vmware/versatile-data-kit/wiki/Ingesting-data-from-DB-into-Database">Ingesting data from DB into Database</a></span><br>
        <span>&#10145;  <a href="https://github.com/vmware/versatile-data-kit/wiki/Ingesting-local-CSV-file-into-Database">Ingesting local CSV file into Database</a></span><br>
        <span>&#10145;  <a href="https://github.com/vmware/versatile-data-kit/blob/main/examples/incremental-ingest-from-db-example/README.md">Incremental ingestion using Job Properties</a></span><br>
    </td>
    <td width="50%" >
        <video controls loop muted preload="metadata" src="https://github.com/vmware/versatile-data-kit/assets/2536458/a46a5ecb-63f7-4b4f-9e2d-099e80522dac" aria-label="30 seconds video tutorial for Data Ingestion"></video>
        <!-- link to the video above https://www.canva.com/design/DAFq7Tc2vNk/3Qfi7ge5nOkEAbAEohEzgw/edit?utm_content=DAFq7Tc2vNk -->
    </td>
  </tr>
</table>








<br/><br/>
<p id="transformation" align="center">
    <a href="#intro"><img src="https://img.shields.io/badge/VDK%20SDK-lightblue" alt="Intro to VDK SDK"></a>
    <a href="#ingestion"><img src="https://img.shields.io/badge/Data%20Ingestion-lightblue" alt="Ingestion"></a>
    <a href="#transformation"><img src="https://img.shields.io/badge/Data%20Transformation-blue" alt="Transformation"></a>
    <a href="#deployment"><img src="https://img.shields.io/badge/Data%20Job%20Deployment-lightblue" alt="Job Deployment"></a>
    <a href="#operations"><img src="https://img.shields.io/badge/Data%20Job%20Operations-lightblue" alt="Job Operations"></a>
    <a href="#plugins"><img src="https://img.shields.io/badge/Lego%20like%20Extensibility-lightblue" alt="Extensibility"></a>
    <a href="#contributing"><img src="https://img.shields.io/badge/Support%20and%20Contributing-lightblue" alt="Support and Contributing"></a>
</p>

<h1>Data Transformation</h1>

<table width="100%" >
  <tr>
    <td width="50%" >
        <ul>
          <li>SQL and Python parameterized transformations.</li>
          <li>Extensible templates for data modeling.</li>
          <li>Creates a dataset or table as a product.</li>
        </ul>
        <hr>
        <p><b>Get started with transforming data:</b></p>
        <span>&#10145;  <a href="https://github.com/vmware/versatile-data-kit/wiki/Data-Modeling-Guide:-Treating-Data-as-a-Product">Data Modeling: Treating Data as a Product</a> </span><br>
        <span>&#10145;  <a href="https://github.com/vmware/versatile-data-kit/wiki/Processing-data-using-SQL-and-local-database">Processing data using SQL and local database</a></span><br>
        <span>&#10145;  <a href="https://github.com/vmware/versatile-data-kit/wiki/SQL-Data-Processing-templates-examples">Processing data using Kimball warehousing templates</a></span><br>
    </td>
    <td width="50%" >
        <video controls loop muted preload="metadata" src="https://github.com/vmware/versatile-data-kit/assets/2536458/56be0a37-257e-4f9d-a558-afd012715dcb" aria-label="30 seconds video tutorial for Data Transformation"></video>
        <!-- link to the video above https://www.canva.com/design/DAFqxoSAXdM/oOG1pB0ekgrCCnKUyaB60Q/edit?utm_content=DAFqxoSAXdM -->
    </td>
  </tr>
</table>








<br/><br/>
<p id="deployment" align="center">
    <a href="#intro"><img src="https://img.shields.io/badge/VDK%20SDK-lightblue" alt="Intro to VDK SDK"></a>
    <a href="#ingestion"><img src="https://img.shields.io/badge/Data%20Ingestion-lightblue" alt="Ingestion"></a>
    <a href="#transformation"><img src="https://img.shields.io/badge/Data%20Transformation-lightblue" alt="Transformation"></a>
    <a href="#deployment"><img src="https://img.shields.io/badge/Data%20Job%20Deployment-blue" alt="Job Deployment"></a>
    <a href="#operations"><img src="https://img.shields.io/badge/Data%20Job%20Operations-lightblue" alt="Job Operations"></a>
    <a href="#plugins"><img src="https://img.shields.io/badge/Lego%20like%20Extensibility-lightblue" alt="Extensibility"></a>
    <a href="#contributing"><img src="https://img.shields.io/badge/Support%20and%20Contributing-lightblue" alt="Support and Contributing"></a>
</p>

<h1>Data Job Deployment (build, deploy, release)</h1>

<table width="100%" >
  <tr>
    <td width="50%" >
        <span>VDK Control Service provides REST API for users to create, deploy, manage, and execute data jobs in a Kubernetes runtime environment.</span>
        <ul>
          <li>Scheduling, packaging, dependencies management, deployment.</li>
          <li>Execution management and monitoring.</li>
          <li>Source code versioning and tracking. Fast rollback.</li>
          <li>Manage state and credentials using Properties and Secrets.</li>
        </ul>
        <hr>
        <p><b>Get started with deploying jobs in control service:</b></p>
        <span>&#10145;  <a href="https://github.com/vmware/versatile-data-kit/wiki/Versatile-Data-Kit-Control-Service#install-locally">Install Local Control Service with vdk server --install</a> </span><br>
        <span>&#10145;  <a href="https://github.com/vmware/versatile-data-kit/wiki/Scheduling-a-Data-Job-for-automatic-execution">Scheduling a Data Job for automatic execution</a></span><br>
        <span>&#10145;  <a href="https://github.com/vmware/versatile-data-kit/wiki/Using-VDK-DAGs-to-orchestrate-data-jobs">Using VDK DAGs to orchestrate Data Jobs</a></span><br>
    </td>
    <td width="50%" >
        <video controls loop muted preload="metadata" src="https://github.com/vmware/versatile-data-kit/assets/2536458/5bf96910-ff27-4ecf-a631-c0e64e1db249" aria-label="30 seconds video tutorial for VDK Control Service"></video>
        <!-- link to the video above https://www.canva.com/design/DAFsIj6BtVY/QMLKEYNGCJZRHSIJmYW99A/edit?utm_content=DAFsIj6BtVY -->
    </td>
  </tr>
</table>











<br/><br/>
<p id="operations" align="center">
    <a href="#intro"><img src="https://img.shields.io/badge/VDK%20SDK-lightblue" alt="Intro to VDK SDK"></a>
    <a href="#ingestion"><img src="https://img.shields.io/badge/Data%20Ingestion-lightblue" alt="Ingestion"></a>
    <a href="#transformation"><img src="https://img.shields.io/badge/Data%20Transformation-lightblue" alt="Transformation"></a>
    <a href="#deployment"><img src="https://img.shields.io/badge/Data%20Job%20Deployment-lightblue" alt="Job Deployment"></a>
    <a href="#operations"><img src="https://img.shields.io/badge/Data%20Job%20Operations-blue" alt="Job Operations"></a>
    <a href="#plugins"><img src="https://img.shields.io/badge/Lego%20like%20Extensibility-lightblue" alt="Extensibility"></a>
    <a href="#contributing"><img src="https://img.shields.io/badge/Support%20and%20Contributing-lightblue" alt="Support and Contributing"></a>
</p>

<h1>Operations and Monitoring</h1>

<table width="100%" >
  <tr>
    <td width="50%" >
        <ul>
          <li>Use Operations UI to monitor, troubleshoot data workloads in production.</li>
          <li>Notifications for errors during Data Job deployment or execution.</li>
          <li>Route errors to correct people by classifying them into User or Platform errors.</li>
        </ul>
        <hr>
        <p><b>Get started with operating and monitoring data jobs:</b></p>
        <span>&#10145;  <a href="https://youtu.be/DLRGCCGUp0U?t=111">Versatile Data Kit UI - Installation and Getting Started</a> </span><br>
        <span>&#10145;  <a href="https://www.youtube.com/watch?v=9BkAOSvXuUg">VDK Operations User Interface - Versatile Data Kit</a></span><br>
    </td>
    <td width="50%" >
        <video controls loop muted preload="metadata" src="https://github.com/vmware/versatile-data-kit/assets/2536458/4e4b5677-267d-4b9b-9b61-65ae7623f161" aria-label="30 seconds video tutorial for VDK Operations UI"></video>
        <!-- link to the video above https://www.canva.com/design/DAFsPZyGThU/nx5DNB7Ybzjx6OEkyjRVBQ/edit?utm_content=DAFsPZyGThU -->
    </td>
  </tr>
</table>






<br/><br/>
<p id="plugins" align="center">
    <a href="#intro"><img src="https://img.shields.io/badge/VDK%20SDK-lightblue" alt="Intro to VDK SDK"></a>
    <a href="#ingestion"><img src="https://img.shields.io/badge/Data%20Ingestion-lightblue" alt="Ingestion"></a>
    <a href="#transformation"><img src="https://img.shields.io/badge/Data%20Transformation-lightblue" alt="Transformation"></a>
    <a href="#deployment"><img src="https://img.shields.io/badge/Data%20Job%20Deployment-lightblue" alt="Job Deployment"></a>
    <a href="#operations"><img src="https://img.shields.io/badge/Data%20Job%20Operations-lightblue" alt="Job Operations"></a>
    <a href="#plugins"><img src="https://img.shields.io/badge/Lego%20like%20Extensibility-blue" alt="Extensibility"></a>
    <a href="#contributing"><img src="https://img.shields.io/badge/Support%20and%20Contributing-lightblue" alt="Support and Contributing"></a>
</p>
<h1>Lego like extensibility</h1>

<table width="100%" >
  <tr>
    <td width="50%" >
        <ul>
          <li>Modular: use only what you need. Extensible: build what you miss.</li>
          <li>Easy to install any plugins as python packages using <code>pip</code>.</li>
          <li>Used in enhancing data processing, ingestion, job execution, command-line lifecycle</li>
        </ul>
        <hr>
        <p><b>Get started with using some VDK plugins:</b></p>
        <span>&#10145;  <a href="https://github.com/vmware/versatile-data-kit/tree/main/projects/vdk-plugins">Browse available plugins</a> </span><br>
        <span>&#10145;  Interesting plugins to check out:</span><br>
        <span>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; <a href="https://github.com/vmware/versatile-data-kit/tree/main/projects/vdk-plugins/vdk-lineage#vdk-lineage">Track Lineage of your jobs using vdk-lineage</a></span><br>
        <span>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; <a href="https://github.com/vmware/versatile-data-kit/tree/main/projects/vdk-plugins/vdk-csv#versatile-data-kit-csv-plugin">Import/Ingest or Export CSV files using vdk-csv</a></span><br>
        <span>&#10145;  <a href="https://github.com/vmware/versatile-data-kit/tree/main/projects/vdk-plugins#write-your-own-plugin">Write your own plugin</a></span><br>
    </td>
    <td width="50%" >
      <video controls loop muted preload="metadata" src="https://github.com/vmware/versatile-data-kit/assets/2536458/2fea5d6e-3fe4-475f-91ec-89838f18ebf3" aria-label="30 seconds video tutorial for VDK Plugins"></video>
        <!-- link to the video above https://www.canva.com/design/DAFsQ3IeJy4/1b2x-HgStJAbztUwGANX5w/edit?utm_content=DAFsQ3IeJy4 -->
    </td>
  </tr>
</table>











<br/><br/>
<p id="contributing" align="center">
    <a href="#intro"><img src="https://img.shields.io/badge/VDK%20SDK-lightblue" alt="Intro to VDK SDK"></a>
    <a href="#ingestion"><img src="https://img.shields.io/badge/Data%20Ingestion-lightblue" alt="Ingestion"></a>
    <a href="#transformation"><img src="https://img.shields.io/badge/Data%20Transformation-lightblue" alt="Transformation"></a>
    <a href="#deployment"><img src="https://img.shields.io/badge/Data%20Job%20Deployment-lightblue" alt="Job Deployment"></a>
    <a href="#operations"><img src="https://img.shields.io/badge/Data%20Job%20Operations-lightblue" alt="Job Operations"></a>
    <a href="#plugins"><img src="https://img.shields.io/badge/Lego%20like%20Extensibility-lightblue" alt="Extensibility"></a>
    <a href="#contributing"><img src="https://img.shields.io/badge/Support%20and%20Contributing-blue" alt="Support and Contributing"></a>
</p>

# Support and Contributing
For Support, you can join our Slack channel, create an [issue](https://github.com/vmware/versatile-data-kit/issues) or [pull request](https://github.com/vmware/versatile-data-kit/pulls) on GitHub to submit suggestions or changes. <br>
If you are interested in contributing as a developer, visit the [contributing](https://github.com/vmware/versatile-data-kit/blob/main/CONTRIBUTING.md) page.

# Contacts
- Message us on Slack:<br>
    ☝️ Join the [CNCF Slack workspace](https://communityinviter.com/apps/cloud-native/cncf).<br>
    ✌️ Join the [#versatile-data-kit](https://cloud-native.slack.com/archives/C033PSLKCPR) channel.
- Join the [next Community Meeting](https://github.com/vmware/versatile-data-kit/wiki/Community-Meetings)
- Follow us on [Twitter](https://twitter.com/VDKProject).
- Subscribe to the [Versatile Data Kit YouTube Channel](https://www.youtube.com/channel/UCasf2Q7X8nF7S4VEmcTHJ0Q).
- Join our [development mailing list](mailto:join-versatiledatakit@groups.vmware.com), used by developers and maintainers of VDK.

# Code of Conduct
Everyone involved in working on the project's source code, or engaging in any issue trackers, Slack channels,
and mailing lists is expected to be familiar with and follow the [Code of Conduct](https://github.com/vmware/versatile-data-kit/blob/main/CODE_OF_CONDUCT.md).
