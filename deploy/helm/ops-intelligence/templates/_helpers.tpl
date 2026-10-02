{{- define "ops-intelligence.name" -}}
{{- .Chart.Name | trunc 63 | trimSuffix "-" -}}
{{- end -}}

{{- define "ops-intelligence.fullname" -}}
{{- printf "%s-%s" .Release.Name (include "ops-intelligence.name" .) | trunc 63 | trimSuffix "-" -}}
{{- end -}}
