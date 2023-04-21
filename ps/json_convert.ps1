function Convert-JsonObject {
    param (
        [Parameter(Mandatory=$true)][object]$JsonObject
    )
    $props = @{}
    $JsonObject | Get-Member -MemberType NoteProperty | ForEach-Object {
        $name = $_.Name
        $value = $JsonObject.$name
        if ($value -is [System.Management.Automation.PSCustomObject]) {
            $value = Convert-JsonObject $value
        } elseif ($value -is [System.Collections.ArrayList]) {
            $newList = @()
            foreach ($item in $value) {
                if ($item -is [System.Management.Automation.PSCustomObject]) {
                    $newList += Convert-JsonObject $item
                } else {
                    $newList += $item
                }
            }
            $value = $newList
        }
        $props.Add($name, $value)
    }
    return New-Object PSObject -Property $props
}

$response = '[{key1:value1, key2:[{key2a:value2a, key2b:value2b}]}]'
$jsonResponse = ConvertFrom-Json $response
$jsonResponse = Convert-JsonObject $jsonResponse
$jsonResponse | Format-Table -AutoSize
