package TMSrestruct;

###################################################################################################
#
# TMSrestruct.pm
#
###################################################################################################

use strict;

use TMSstr;
use TMScommon;

###################################################################################################

sub need_restruction_page
{
  my ( $url) = @_;

  my $lang = &TMSstr::get_lang();

  my $str_NEED_RESTRUCTION_FIRST = &TMSstr::get_str( "NEED_RESTRUCTION_FIRST"	);
  my $str_KEEP_GOING		 = &TMSstr::get_str( "KEEP_GOING"		);
  my $str_BACK			 = &TMSstr::get_str( "BACK"			);

  my $tbl_width = 630;
  my $menu_color = '#ED1C24';
  my $body_color = '#FDE1D4';

  my $cgifile = '../edit/apply.cgi';
  my $title         = &TMSstr::get_str( "NOT_RESTRUCTION" );
  my $submit_button = &TMSstr::get_str( "REPORT_DATA_RESTRUCTION" );

  my $html = 	"<html lang=$lang>\n".
		"<head>\n".
		"<STYLE TYPE=\"text/css\">\n".
		"A:link    { color: Midnightblue }\n".
		"A:visited { color: Midnightblue }\n".
		"A:active  { color: Red }\n".
		"</STYLE>\n".
		&TMScommon::meta_content_type( $lang ).
		&TMScommon::meta_no_cache_tag().
		"<title>$title</title>\n".
		"<script language=JavaScript>\n".
		"<!--\n".
		"  var submit_disflg = 0;\n".
		"  function disable_submit() {\n".
		"    document.fminput.submit.disabled = true;\n".
		"    if(submit_disflg==0){\n".
		"      submit_disflg = 1;\n".
		"      return true;\n".
		"    }else{\n".
		"      return false;\n".
		"    }\n".
		"  }\n".
		"//-->\n".
		"</script>\n".
		"</head>\n".
		"<body bgcolor=#C7C4E2><center>\n".
		&TMScommon::make_header('menu','dummy', $lang)."<BR>".

		"<table border=1 frame=box width=$tbl_width cellPadding=6>\n".
		"<tr align=center bgcolor=$menu_color>\n".
		"<th><font size=+2 color=white>$title</font></th>\n".
		"</tr>\n".
		"<tr align=center bgcolor=$body_color><td>\n".
		"<BR><BR><BR>\n".
		"<font size=+1><B>$str_NEED_RESTRUCTION_FIRST</B></font>\n".
		"<BR><BR><BR><BR>\n".
		"<B>\n".
		"<A HREF=$url>&lt&nbsp;$str_KEEP_GOING&nbsp;&gt</A>&nbsp;&nbsp;&nbsp;&nbsp;".
		"<A HREF=\"javascript:history.back()\">&lt&nbsp;$str_BACK&nbsp;&gt</A>\n".
		"</B>\n".
		"<BR><BR><BR>\n".

		"<form name=\"fminput\" action=\"$cgifile\" method=POST onSubmit=\"return disable_submit()\">\n".
		"<input type=SUBMIT name=\"submit\" value=\"$submit_button\">\n".
		"<BR><BR></form>\n".

		"</td></tr>\n".
		"</table><BR>\n".

		&TMScommon::make_footer('dummy','menu', $lang).
		"</center></body></html>\n";
  return $html;
}

###################################################################################################

my $restruction_req = "..\\..\\tmsdata\\restruction.req";

sub check_restruction
{
  # データ再構築要求ファイル
  if( -f $restruction_req ){ return 1; }

  # データバージョンが古い
  if( -d "..\\..\\tmsdata\\shift" ){
    unless( -d "..\\..\\tmsdata\\shift-shift" ){ return 1; }
  }

  return 0;
}

#------------------------------------------------------------

sub request_restruction
{
  if( open(REQ, "> $restruction_req") ){
    print REQ "restruction request\n";
    close(REQ);
  }
}

#------------------------------------------------------------

sub clr_restruction_request
{
  if( -f $restruction_req ){ unlink($restruction_req); }
}

###################################################################################################
1;
