# Dependencies & INVESTIGATE / INCOMPATIBLE

Packages needing manual manifest/dependency review, plus Qualcomm-bound packages replaced by base equivalents.

Total: **60** packages

| Package | Class | Location | Justification |
|---|---|---|---|
| `com.android.avatarpicker` | INVESTIGATE | `system_ext/priv-app/AvatarPicker/AvatarPicker.apk` | Purpose/dependencies unclear — manual manifest review required |
| `com.android.bluetooth.oplus.overlay` | INCOMPATIBLE | `system_ext/overlay/OplusBluetoothResource.apk` | Qualcomm/SoC-specific; raven uses Tensor vendor — base (LineageOS) equivalent must be used instead |
| `com.android.intentresolver` | INVESTIGATE | `system/system/priv-app/IntentResolver/IntentResolver.apk` | Purpose/dependencies unclear — manual manifest review required |
| `com.android.statementservice` | INVESTIGATE | `product/priv-app/StatementService/StatementService.apk` | Purpose/dependencies unclear — manual manifest review required |
| `com.fido.asm` | INVESTIGATE | `system_ext/app/FidoAsm/FidoAsm.apk` | Purpose/dependencies unclear — manual manifest review required |
| `com.fido.uafclient` | INVESTIGATE | `system_ext/app/UAFClient/UAFClient/UAFClient.apk` | Purpose/dependencies unclear — manual manifest review required |
| `com.microsoftsdk.crossdeviceservicebroker` | INVESTIGATE | `system/system/app/CrossDeviceServiceBroker/CrossDeviceServiceBroker.apk` | Purpose/dependencies unclear — manual manifest review required |
| `com.oplus.acc.gac` | INVESTIGATE | `system_ext/app/CloudAccService/CloudAccService.apk` | Purpose/dependencies unclear — manual manifest review required |
| `com.oplus.atlas` | INVESTIGATE | `system_ext/app/OplusAtlasService/OplusAtlasService.apk` | Region-specific (CN) service — verify dependency on Settings/Launcher/AI/FluidCloud before any removal (§B) |
| `com.oplus.beidouservice` | INVESTIGATE | `system_ext/priv-app/BeidouMsgService/BeidouMsgService.apk` | Region-specific (CN) service — verify dependency on Settings/Launcher/AI/FluidCloud before any removal (§B) |
| `com.oplus.bttestmode` | INVESTIGATE | `system_ext/app/BTtestmode/BTtestmode.apk` | Engineering/factory/trial mode — candidate for removal per policy §A; verify no system dependency first |
| `com.oplus.eid` | INVESTIGATE | `system_ext/app/EidService/EidService.apk` | Region-specific (CN) service — verify dependency on Settings/Launcher/AI/FluidCloud before any removal (§B) |
| `com.oplus.engineercamera` | INVESTIGATE | `system_ext/app/OplusCommercialEngineerCamera/OplusCommercialEngineerCamera.apk` | Engineering/factory/trial mode — candidate for removal per policy §A; verify no system dependency first |
| `com.oplus.engineermode` | INVESTIGATE | `system_ext/app/OplusCommercialEngineerMode/OplusCommercialEngineerMode.apk` | Engineering/factory/trial mode — candidate for removal per policy §A; verify no system dependency first |
| `com.oplus.engineernetwork` | INVESTIGATE | `system_ext/app/OplusEngineerNetwork/OplusEngineerNetwork.apk` | Engineering/factory/trial mode — candidate for removal per policy §A; verify no system dependency first |
| `com.oplus.logtrial` | INVESTIGATE | `system_ext/app/LogTrialCommercial/LogTrialCommercial.apk` | Engineering/factory/trial mode — candidate for removal per policy §A; verify no system dependency first |
| `com.oplus.nas.acc` | INVESTIGATE | `system_ext/app/NetworkAssistSys_plugin_CellularAcc/NetworkAssistSys_plugin_CellularAcc.apk` | Region-specific (CN) service — verify dependency on Settings/Launcher/AI/FluidCloud before any removal (§B) |
| `com.oplus.nas.data` | INVESTIGATE | `system_ext/app/NetworkAssistSys_plugin_CellularData/NetworkAssistSys_plugin_CellularData.apk` | Region-specific (CN) service — verify dependency on Settings/Launcher/AI/FluidCloud before any removal (§B) |
| `com.oplus.nas.dds` | INVESTIGATE | `system_ext/app/NetworkAssistSys_plugin_CellularDataSwitch/NetworkAssistSys_plugin_CellularDataSwitch.apk` | Region-specific (CN) service — verify dependency on Settings/Launcher/AI/FluidCloud before any removal (§B) |
| `com.oplus.nas.network` | INVESTIGATE | `system_ext/app/NetworkAssistSys_plugin_CellularNetwork/NetworkAssistSys_plugin_CellularNetwork.apk` | Region-specific (CN) service — verify dependency on Settings/Launcher/AI/FluidCloud before any removal (§B) |
| `com.oplus.nas.recovery` | INVESTIGATE | `system_ext/app/NetworkAssistSys_plugin_CellularReg/NetworkAssistSys_plugin_CellularReg.apk` | Region-specific (CN) service — verify dependency on Settings/Launcher/AI/FluidCloud before any removal (§B) |
| `com.oplus.nas.smartcommu` | INVESTIGATE | `system_ext/app/NetworkAssistSys_plugin_CellularQoE/NetworkAssistSys_plugin_CellularQoE.apk` | Region-specific (CN) service — verify dependency on Settings/Launcher/AI/FluidCloud before any removal (§B) |
| `com.oplus.nas.virtualdata` | INVESTIGATE | `system_ext/app/NetworkAssistSys_plugin_CellularVirtualData/NetworkAssistSys_plugin_CellularVirtualData.apk` | Region-specific (CN) service — verify dependency on Settings/Launcher/AI/FluidCloud before any removal (§B) |
| `com.oplus.nas.voice` | INVESTIGATE | `system_ext/app/NetworkAssistSys_plugin_CellularCall/NetworkAssistSys_plugin_CellularCall.apk` | Region-specific (CN) service — verify dependency on Settings/Launcher/AI/FluidCloud before any removal (§B) |
| `com.oplus.nearcomm` | INVESTIGATE | `system_ext/priv-app/OplusNearComm/OplusNearComm.apk` | Purpose/dependencies unclear — manual manifest review required |
| `com.oplus.nfcengineertest` | INVESTIGATE | `system_ext/app/NfcEngineerTest/NfcEngineerTest/NfcEngineerTest.apk` | Engineering/factory/trial mode — candidate for removal per policy §A; verify no system dependency first |
| `com.oplus.nhs` | INVESTIGATE | `system_ext/app/NetworkHealthService/NetworkHealthService.apk` | Purpose/dependencies unclear — manual manifest review required |
| `com.oplus.nrMode` | INVESTIGATE | `system_ext/priv-app/OplusNrMode/OplusNrMode.apk` | Purpose/dependencies unclear — manual manifest review required |
| `com.oplus.owkservice` | INVESTIGATE | `system_ext/app/OwkService/OwkService.apk` | Region-specific (CN) service — verify dependency on Settings/Launcher/AI/FluidCloud before any removal (§B) |
| `com.oplus.postmanservice` | INVESTIGATE | `system_ext/app/PostmanService/PostmanService.apk` | Region-specific (CN) service — verify dependency on Settings/Launcher/AI/FluidCloud before any removal (§B) |
| `com.oplus.powermonitor` | INVESTIGATE | `system_ext/app/PowerMonitor/PowerMonitor.apk` | Purpose/dependencies unclear — manual manifest review required |
| `com.oplus.rsmcsatellite` | INVESTIGATE | `system_ext/app/RsmcSatelliteAuth/RsmcSatelliteAuth.apk` | Region-specific (CN) service — verify dependency on Settings/Launcher/AI/FluidCloud before any removal (§B) |
| `com.oplus.sau` | INVESTIGATE | `system_ext/app/SystemAppUpdateService/SystemAppUpdateService.apk` | Region-specific (CN) service — verify dependency on Settings/Launcher/AI/FluidCloud before any removal (§B) |
| `com.oplus.sauhelper` | INVESTIGATE | `system_ext/app/SAUHelper/SAUHelper.apk` | Region-specific (CN) service — verify dependency on Settings/Launcher/AI/FluidCloud before any removal (§B) |
| `com.oplus.trafficmonitor` | INVESTIGATE | `system_ext/priv-app/TrafficMonitor/TrafficMonitor.apk` | Purpose/dependencies unclear — manual manifest review required |
| `com.oplus.ttsatellite` | INVESTIGATE | `system_ext/app/TTSatelliteAuth/TTSatelliteAuth.apk` | Region-specific (CN) service — verify dependency on Settings/Launcher/AI/FluidCloud before any removal (§B) |
| `com.oplus.virtualcomm` | INVESTIGATE | `system_ext/priv-app/OplusVirtualComm/OplusVirtualComm.apk` | Purpose/dependencies unclear — manual manifest review required |
| `com.oplus.virtualcomm2` | INVESTIGATE | `system_ext/priv-app/VirtualCommService/VirtualCommService.apk` | Purpose/dependencies unclear — manual manifest review required |
| `com.oplus.voice.crs` | INVESTIGATE | `system_ext/app/CrsVcrbtSwitch/CrsVcrbtSwitch.apk` | Region-specific (CN) service — verify dependency on Settings/Launcher/AI/FluidCloud before any removal (§B) |
| `com.qti.dcf` | INCOMPATIBLE | `system_ext/priv-app/dcf/dcf.apk` | Qualcomm/SoC-specific; raven uses Tensor vendor — base (LineageOS) equivalent must be used instead |
| `com.qti.dpmserviceapp` | INCOMPATIBLE | `system_ext/priv-app/dpmserviceapp/dpmserviceapp.apk` | Qualcomm/SoC-specific; raven uses Tensor vendor — base (LineageOS) equivalent must be used instead |
| `com.qti.overlay.framework.nonmodem` | INCOMPATIBLE | `product/overlay/FrameworksResNonModem_Sys.apk` | Qualcomm/SoC-specific; raven uses Tensor vendor — base (LineageOS) equivalent must be used instead |
| `com.qti.qcc` | INCOMPATIBLE | `system_ext/app/QCC/QCC.apk` | Qualcomm/SoC-specific; raven uses Tensor vendor — base (LineageOS) equivalent must be used instead |
| `com.qualcomm.atfwd` | INCOMPATIBLE | `system_ext/app/atfwd/atfwd.apk` | Qualcomm/SoC-specific; raven uses Tensor vendor — base (LineageOS) equivalent must be used instead |
| `com.qualcomm.location` | INCOMPATIBLE | `system_ext/priv-app/com.qualcomm.location/com.qualcomm.location.apk` | Qualcomm/SoC-specific; raven uses Tensor vendor — base (LineageOS) equivalent must be used instead |
| `com.qualcomm.qcrilmsgtunnel` | INCOMPATIBLE | `system_ext/priv-app/qcrilmsgtunnel/qcrilmsgtunnel.apk` | Qualcomm/SoC-specific; raven uses Tensor vendor — base (LineageOS) equivalent must be used instead |
| `com.qualcomm.qti.powersavemode` | INCOMPATIBLE | `system_ext/app/PowerSaveMode/PowerSaveMode.apk` | Qualcomm/SoC-specific; raven uses Tensor vendor — base (LineageOS) equivalent must be used instead |
| `com.qualcomm.qti.telephonyservice` | INCOMPATIBLE | `system_ext/app/QtiTelephonyService/QtiTelephonyService.apk` | Qualcomm/SoC-specific; raven uses Tensor vendor — base (LineageOS) equivalent must be used instead |
| `com.qualcomm.qti.workloadclassifier` | INCOMPATIBLE | `system_ext/app/workloadclassifier/workloadclassifier.apk` | Qualcomm/SoC-specific; raven uses Tensor vendor — base (LineageOS) equivalent must be used instead |
| `com.qualcomm.qti.xrcb` | INCOMPATIBLE | `system_ext/priv-app/xrcbservice/xrcbservice.apk` | Qualcomm/SoC-specific; raven uses Tensor vendor — base (LineageOS) equivalent must be used instead |
| `com.qualcomm.qti.xrvd.service` | INCOMPATIBLE | `system_ext/priv-app/xrvdservice/xrvdservice.apk` | Qualcomm/SoC-specific; raven uses Tensor vendor — base (LineageOS) equivalent must be used instead |
| `com.qualcomm.uimremoteclient` | INCOMPATIBLE | `product/app/uimremoteclient/uimremoteclient.apk` | Qualcomm/SoC-specific; raven uses Tensor vendor — base (LineageOS) equivalent must be used instead |
| `com.qualcomm.uimremoteserver` | INCOMPATIBLE | `product/app/uimremoteserver/uimremoteserver.apk` | Qualcomm/SoC-specific; raven uses Tensor vendor — base (LineageOS) equivalent must be used instead |
| `com.qualcomm.wfd.service` | INCOMPATIBLE | `system_ext/priv-app/WfdService/WfdService.apk` | Qualcomm/SoC-specific; raven uses Tensor vendor — base (LineageOS) equivalent must be used instead |
| `com.tencent.soter.soterserver` | INVESTIGATE | `system_ext/app/SoterService/SoterService.apk` | Region-specific (CN) service — verify dependency on Settings/Launcher/AI/FluidCloud before any removal (§B) |
| `com.wapi.wapicertmanage` | INCOMPATIBLE | `system_ext/app/WapiCertManage/WapiCertManage.apk` | Qualcomm/SoC-specific; raven uses Tensor vendor — base (LineageOS) equivalent must be used instead |
| `org.codeaurora.ims` | INCOMPATIBLE | `system_ext/priv-app/ims/ims.apk` | Qualcomm/SoC-specific; raven uses Tensor vendor — base (LineageOS) equivalent must be used instead |
| `vendor.qti.data.ntnsatapp` | INCOMPATIBLE | `system_ext/app/NtnSatApp/NtnSatApp.apk` | Qualcomm/SoC-specific; raven uses Tensor vendor — base (LineageOS) equivalent must be used instead |
| `vendor.qti.frameworks.utils` | INCOMPATIBLE | `system_ext/app/FrameworksUtilsSysService/FrameworksUtilsSysService.apk` | Qualcomm/SoC-specific; raven uses Tensor vendor — base (LineageOS) equivalent must be used instead |
| `vendor.qti.imsdatachannel` | INCOMPATIBLE | `system_ext/app/ImsDataChannelService/ImsDataChannelService.apk` | Qualcomm/SoC-specific; raven uses Tensor vendor — base (LineageOS) equivalent must be used instead |
