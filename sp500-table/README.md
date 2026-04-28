<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>S&P 500 — Full Table</title>

<style>
    body {
        font-family: Arial, sans-serif;
        background: #ffffff;
        margin: 40px;
        color: #222;
    }

    h1 {
        font-size: 28px;
        margin-bottom: 20px;
        font-weight: 600;
    }

    table {
        width: 100%;
        border-collapse: collapse;
        font-size: 14px;
    }

    thead th {
        position: sticky;
        top: 0;
        background: #f7f7f7;
        padding: 10px;
        border-bottom: 2px solid #ddd;
        z-index: 2;
    }

    tbody td {
        padding: 8px 10px;
        border-bottom: 1px solid #e5e5e5;
    }

    a {
        color: #0056b3;
        text-decoration: none;
        font-weight: 600;
    }

    a:hover {
        text-decoration: underline;
    }

    /* Tons neutros por setor */
    .sector-Industrials { background: #f2f2f2; }
    .sector-HealthCare { background: #f4f4f4; }
    .sector-InformationTechnology { background: #f1f1f1; }
    .sector-Utilities { background: #f3f3f3; }
    .sector-Financials { background: #efefef; }
    .sector-ConsumerDiscretionary { background: #f5f5f5; }
    .sector-ConsumerStaples { background: #f0f0f0; }
    .sector-RealEstate { background: #f6f6f6; }
    .sector-Energy { background: #ededed; }
    .sector-CommunicationServices { background: #f8f8f8; }
    .sector-Materials { background: #eaeaea; }
</style>
</head>

<body>

<h1>S&P 500 — Full Company Table</h1>

<table>
<thead>
<tr>
    <th>Symbol</th>
    <th>Security</th>
    <th>GICS Sector</th>
    <th>GICS Sub-Industry</th>
</tr>
</thead>

<tbody>
