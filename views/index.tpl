<!DOCTYPE HTML>
<html>
<head>
<style>
body {
    padding:10px;
}
select {
    width:120px;
}
</style>
<meta charset="UTF-8">
</head>
<body>
<h2>finder</h2>
<form method="GET" action="/find/">
<select name="type">
<option value="bc">barcode</option>
<option value="bib">bib id</option>
<option value="item">item id</option>
<option value="auth">author</option>
<option value="call">call no</option>
</select>
<input name="num" type="text" value=""/>
<input type="submit" value="go" />
<form>
</body>
</html>
