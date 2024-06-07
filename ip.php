<?php
function ipRange($start, $end) {
    $range = [];
    $start = ip2long($start);
    $end = ip2long($end);
    for ($ip = $start; $ip <= $end; $ip++) {
        $range[] = long2ip($ip);
    }
    return $range;
}

$ip_list = ipRange("10.208.0.0", "10.208.3.255");

// Convertir le tableau en une chaîne de caractères, chaque IP séparée par une virgule
echo implode(",", $ip_list);
?>
