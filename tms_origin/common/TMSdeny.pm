package TMSdeny;

###################################################################################################
#
# TMSdeny.pm
#
###################################################################################################

use strict;

use TMSstr;
use TMScommon;

###################################################################################################

sub is_demo_mode
{
  return 0;	# (号口)→不許可ページを表示
#  return 1;	# (デモ)→画面表示するが、サブミットボタン disabled
}

###################################################################################################

sub permission_deny_page
{
  my $lang = &TMSstr::get_lang();

  my $title    = &TMSstr::get_str( "PERMISSION_DENY" );
  my $str_BACK = &TMSstr::get_str( "BACK" );
  my $str_CANT_ACCESS_THIS_PAGE_FROM_REMOTE = &TMSstr::get_str( "CANT_ACCESS_THIS_PAGE_FROM_REMOTE" );

  my $tbl_width = 630;
  my $menu_color = '#ED1C24';
  my $body_color = '#FDE1D4';

  my $html =	"<html lang=$lang>\n".
		"<head>\n".
		&TMScommon::meta_content_type( $lang ).
		&TMScommon::meta_no_cache_tag().
		"<title>$title</title>\n".
		"</head>\n".
		"<body bgcolor=#C7C4E2><center>\n".
		&TMScommon::make_header('menu','dummy', $lang)."<BR>".

		"<table border=1 frame=box width=$tbl_width cellPadding=6>\n".
		"<tr align=center bgcolor=$menu_color>\n".
		"<th><font size=+2 color=white>$title</font></th>\n".
		"</tr>\n".
		"<tr align=center bgcolor=$body_color><td>\n".
		"<BR><BR><BR>\n".
		"<font size=+2><B>$str_CANT_ACCESS_THIS_PAGE_FROM_REMOTE</B></font>\n".
		"<BR><BR><BR>\n".
		"<A HREF=\"javascript:history.back()\"><IMG SRC=\"../image/back2_$lang.jpg\" width=85 height=27 alt=\"$str_BACK\" border=0></A>\n".
		"<BR><BR><BR><BR>\n".
		"</td></tr>\n".
		"</table><BR>\n".

		&TMScommon::make_footer('dummy','menu', $lang).
		"</center></body></html>\n";

  return $html;
}

###################################################################################################
1;
