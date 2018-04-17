<!DOCTYPE html>

<html>
  <head>
    <title>result</title>
    <style>
		body{
			padding:10px;
		}
		table {
			margin:10px;
                        border-collapse:collapse;
		}
	    td, th {
			border:1px solid #ddd;
			padding:5px;
		}
		tr:nth-child(2) {
			background-color:#FFFF66;
		}	
	</style>
	<meta charset="UTF-8">
  </head>
  <body>
<a href='/find/'>back</a>
  <h2>bib: {{bib}}</h2>
  <p><b>ti:</b> {{ti}}</p>
  <p><b>902:</b> {{f902}}</p>
% if fields:
 <table><tr><th>date</th><th>action</th><th>item status</th><th>initials</th><th>location</th><th>unit</th></tr>
    %for field in fields:
        <tr><td>{{field[1]}}</td><td>{{field[8]}}</td><td>{{field[9]}}</td><td>{{field[2]}}</td><td>{{field[5]}}</td><td>{{field[6]}}</td></tr>	
    %end
    </table>
% else:
  <h4>No bib history.</h4>
% end

% if itm is not None:
 <h2>item: {{itm}}</h2>
%end
% if bc is not None:
 <p><b>bc:</b> {{bc}}</p>
%end
% if status is not None:
<table><tr><th>item id</th><th>status</th><th>status date</th><th>create operator</th><th>create date</th><th>modify operator</th><th>modify date</th></tr>
%for s in status:
<tr><td>{{s[0]}}</td><td>{{s[1]}}</td><td>{{s[2]}}</td><td>{{s[3]}}</td><td>{{s[4]}}</td><td>{{s[5]}}</td><td>{{s[6]}}</td></tr>
%end 
</table>
%end
  </body>
</html>
