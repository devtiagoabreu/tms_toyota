#! C:\Perl\bin\perl.exe -I..\common

use strict;
no strict "refs";	# for open($fd,'httpc.exe |')
use CGI;
use CGI::Carp qw(fatalsToBrowser);

use TMSstr;
use TMScommon;
use TMSselitem;
use TMSipset;
use TMSscanner;

require '../common/http_header.pm';

my $lang = &TMSstr::get_lang_set();
&TMSstr::load_str_file($lang);       # �K�� get_str() �̑O�Ɏ��s���鎖�I�I

my $str_UPDATE_SETTING		= &TMSstr::get_str( 'UPDATE_SETTING'	);
my $str_UPDATE_OK		= &TMSstr::get_str( 'UPDATE_OK'		);

my $str_LOOM_NAME		= &TMSstr::get_str( "LOOM_NAME"		);
my $str_STYLE_NAME		= &TMSstr::get_str( "STYLE_NAME"	);

my $str_OPERATION_STATUS 	= &TMSstr::get_str( 'OPERATION_STATUS'	);

my $str_PAGE			= &TMSstr::get_str( 'PAGE'		);
my $str_REFRESH			= &TMSstr::get_str( 'REFRESH'		);

my $str_STATUS			= &TMSstr::get_str( 'STATUS'		);
my $str_DURATION		= &TMSstr::get_str( 'DURATION'		);
my $str_STOP_COUNT		= &TMSstr::get_str( 'STOP_COUNT'	);
my $str_EFFICIENCY		= &TMSstr::get_str( 'EFFICIENCY'	);
my $str_CURRENT_SHIFT		= &TMSstr::get_str( 'CURRENT_SHIFT'	);
my $str_RPM			= &TMSstr::get_str( 'RPM'		);
my $str_DOFFING_FORECAST	= &TMSstr::get_str( 'DOFFING_FORECAST'	);
my $str_WARP_OUT_FORECAST	= &TMSstr::get_str( 'WARP_OUT_FORECAST'	);
my $str_LOWER			= &TMSstr::get_str( 'LOWER'		);
my $str_UPPER			= &TMSstr::get_str( 'UPPER'		);
my $str_HH_MM			= &TMSstr::get_str( 'HH_MM'		);

my $str_SHRINKAGE		= &TMSstr::get_str( 'SHRINKAGE'		);
my $str_UPPER_BEAM		= &TMSstr::get_str( 'UPPER_BEAM'	);
my $str_LOWER_BEAM		= &TMSstr::get_str( 'LOWER_BEAM'	);
my $str_SET_LENGTH		= &TMSstr::get_str( 'SET_LENGTH'	);

my $str_SETTING_RESULT		= &TMSstr::get_str( "SETTING_RESULT"	);
my $str_SETTING_SUCCEED		= &TMSstr::get_str( "SETTING_SUCCEED"	);
my $str_MENU			= &TMSstr::get_str( "MENU"		);
my $str_BACK			= &TMSstr::get_str( "BACK"		);

my %str_status = ( 'Run'             => &TMSstr::get_str( 'OPST__RUN'		),
		   'Out_of_product'  => &TMSstr::get_str( 'OPST__OUT_OF_PRODUCT'),
		   'Warp_out'        => &TMSstr::get_str( 'OPST__WARP_OUT'	),
		   'Cloth_doffing'   => &TMSstr::get_str( 'OPST__CLOTH_DOFFING'	),
		   'Machine_failure' => &TMSstr::get_str( 'OPST__MACHINE_FAILURE'),
		   'Cloth_mending'   => &TMSstr::get_str( 'OPST__CLOTH_MENDING'	),
		   'Power_off'       => &TMSstr::get_str( 'OPST__POWER_OFF'	),
		   'Warp_top'        => &TMSstr::get_str( 'OPST__WARP_TOP'	),
		   'Warp'            => &TMSstr::get_str( 'OPST__WARP'		),
		   'False_selvage'   => &TMSstr::get_str( 'OPST__FALSE_SELVAGE'	),
		   'CatchCode_front' => &TMSstr::get_str( 'OPST__CC_FRONT'	),
		   'CatchCode_rear'  => &TMSstr::get_str( 'OPST__CC_REAR'	),
		   'Leno_L'          => &TMSstr::get_str( 'OPST__LENO_L'	),
		   'Leno_R'          => &TMSstr::get_str( 'OPST__LENO_R'	),
		   'Weft'            => &TMSstr::get_str( 'OPST__WEFT'		),
		   'Manual'          => &TMSstr::get_str( 'OPST__MANUAL'	),
		   'Other'           => &TMSstr::get_str( 'OPST__OTHER'		),
		   'Comm_error'	     => &TMSstr::get_str( 'OPST__COMM_ERR'	),
		   'Not_support'     => &TMSstr::get_str( 'OPST__NOT_SUPPORT'	),
		   'Data_error'	     => &TMSstr::get_str( 'OPST__DATA_ERR'	),
		   'System_error'    => 'System Error' );


my %bg_color = ( 'Run'             => '#dddddd',
		 'Out_of_product'  => '#000000',
		 'Warp_out'        => '#9933cc',
		 'Cloth_doffing'   => '#ff33cc',
		 'Machine_failure' => '#0000ff',
		 'Cloth_mending'   => '#33ccff',
		 'Power_off'       => '#996600',
		 'Warp_top'        => '#ff0000',
		 'Warp'            => '#ff0000',
		 'False_selvage'   => '#ffff00',
		 'CatchCode_front' => '#ffff00',
		 'CatchCode_rear'  => '#ffff00',
		 'Leno_L'          => '#ffff00',
		 'Leno_R'          => '#ffff00',
		 'Weft'            => '#33cc33',
		 'Manual'          => '#ffcc99',
		 'Other'           => '#ffffff',
		 'Comm_error'      => '#000000',
		 'Not_support'     => '#000000',
		 'Data_error'      => '#000000',
		 'System_error'    => '#000000' );


my %font_color = ( 'Run'             => '#999999',
		   'Out_of_product'  => '#ffffff',
		   'Warp_out'        => '#ffffff',
		   'Cloth_doffing'   => '#ffffff',
		   'Machine_failure' => '#ffffff',
		   'Cloth_mending'   => '#000000',
		   'Power_off'       => '#ffffff',
		   'Warp_top'        => '#ffffff',
		   'Warp'            => '#ffffff',
		   'False_selvage'   => '#000000',
		   'CatchCode_front' => '#000000',
		   'CatchCode_rear'  => '#000000',
		   'Leno_L'          => '#000000',
		   'Leno_R'          => '#000000',
		   'Weft'            => '#ffffff',
		   'Manual'          => '#000000',
		   'Other'           => '#000000',
		   'Comm_error'	     => '#ff0000',
		   'Not_support'     => '#ff0000',
		   'Data_error'	     => '#ff0000',
		   'System_error'    => '#ff0000' );


################################################################

## �P�y�[�W�̍ő�\���䐔
use constant LOOM_DISP_MAX => 100;


my $html = new CGI;

## �V�X�e���S�̂́A�@��ID�E�@�䖼�̃��X�g���擾
my @loom_id_name = &get_loom_id_name_list();

## �@�䖼�A�@��ID���Ƀ\�[�g
@loom_id_name = sort { "$$a[1] $$a[0]" cmp "$$b[1] $$b[0]" } @loom_id_name;

## �_�u���r�[����\�����邩�ǂ���
my $beam_type = &TMSselitem::get_value_of_beam_type();


## �\������y�[�W�̔��f
my $page_max = ($#loom_id_name + 1) / LOOM_DISP_MAX;
if( $page_max > int($page_max) ){ $page_max = int($page_max) + 1; }

my $page = 1;
for( my $n=1; $n<=$page_max; $n++ ){
  if( defined($html->param("page$n")) ){
    $page = $n;
    last;
  }
}

## �\���Ώۂ̃f�[�^�͈�
my $disp_start = LOOM_DISP_MAX * ($page -1);
my $disp_end   = LOOM_DISP_MAX * $page;
if( $disp_end > ($#loom_id_name +1) ){ $disp_end = ($#loom_id_name +1); }


##########################################################################
# �\���Ώۂ̋@��̃f�[�^���擾

my @scan1_loom = ();
my @scan2_loom = ();
my @scan3_loom = ();
my @scan4_loom = ();
my @scan5_loom = ();
my @jat710_loom = ();

for( my $i=$disp_start; $i<$disp_end; $i++ ){
  my ($id, $name) = @{$loom_id_name[$i]};

  if( $id =~ m/^S([1-5])-/ ){
    if(    $1 == 1 ){ push( @scan1_loom, $id ); }
    elsif( $1 == 2 ){ push( @scan2_loom, $id ); }
    elsif( $1 == 3 ){ push( @scan3_loom, $id ); }
    elsif( $1 == 4 ){ push( @scan4_loom, $id ); }
    elsif( $1 == 5 ){ push( @scan5_loom, $id ); }
  }
  else{
    push( @jat710_loom, $id );
  }
}

my @scan_ip = &TMSscanner::get_scan_ip();

my %loom_status = ();

if( $#scan1_loom >= 0 ){
  &get_scan_loom_status( $scan_ip[0], \@scan1_loom, \%loom_status );
}
if( $#scan2_loom >= 0 ){
  &get_scan_loom_status( $scan_ip[1], \@scan2_loom, \%loom_status );
}
if( $#scan3_loom >= 0 ){
  &get_scan_loom_status( $scan_ip[2], \@scan3_loom, \%loom_status );
}
if( $#scan4_loom >= 0 ){
  &get_scan_loom_status( $scan_ip[3], \@scan4_loom, \%loom_status );
}
if( $#scan5_loom >= 0 ){
  &get_scan_loom_status( $scan_ip[4], \@scan5_loom, \%loom_status );
}

if( $#jat710_loom >= 0 ){
  &get_jat710_loom_status( \@jat710_loom, \%loom_status );
}


##########################################################################

my $tbl_width = 630;

my $title = $str_OPERATION_STATUS;
my $cgifile = 'opestate.cgi';
my $menu_color = '#fdb913';
my $body_color = '#fff2dd';

print	"<html lang=$lang>\n".
	"<head>\n".
	&TMScommon::meta_content_type( $lang ).
	&TMScommon::meta_no_cache_tag().
	"<title>$title</title>\n".
  "<meta http-equiv=refresh content=60 />\n".
  #"<link href='https://cdn.jsdelivr.net/npm/bootstrap/dist/css/bootstrap.min.css' rel='stylesheet' integrity='sha384-QWTKZyjpPEjISv5WaRU9OFeRpok6YctnYmDr5pNlyT2bRjXh0JMhjY6hW+ALEwIH' crossorigin='anonymous'>\n".
	#"<script src='https://cdn.jsdelivr.net/npm/bootstrap/dist/js/bootstrap.bundle.min.js' integrity='sha384-YvpcrYf0tY3lHB60NNkmXc5s9fDVZLESaAA55NDzOxhy9GkcIdslK1eN7N6jIeHz' crossorigin='anonymous'></script>\n".
  "</head>\n".
	"<body bgcolor=#C7C4E2><center>\n".
	#&TMScommon::make_header
  (
  #  'menu','dummy', 
  #$lang
  )
  ."<BR>\n";

#print	"<form name=\"fminput\" action=\"$cgifile\" method=POST>\n".
#	"<table width=$tbl_width><tr><th nowrap><font size=+2>$title\n".
#	"<input type=SUBMIT name=\"page$page\" value=\"$str_REFRESH\"></font></th></tr></table>\n";

#### �y�[�W�ؑփ{�^�� ####
use constant PAGE_BUTTON_COLUMN_MAX => 5;

if( $page_max > 1 ){
  print	"<table class='table table-dark table-striped'>\n";

  my $col_max;
  if( $page_max < PAGE_BUTTON_COLUMN_MAX ){ $col_max = $page_max; }
  else{ $col_max = PAGE_BUTTON_COLUMN_MAX; }

  my $n = 1;
  while( $n <= $page_max ){
    print "<tr align=center>\n";
    for (my $j=0; $j<$col_max; $j++ ){
      if( $n <= $page_max ){
        if( $n eq $page ){
          print "<td bgcolor=gray><input type=SUBMIT name=\"page$n\" value=\"$str_PAGE $n\" disabled></td>\n";
        }else{
          print "<td><input type=SUBMIT name=\"page$n\" value=\"$str_PAGE $n\"></td>\n";
        }
      }else{ print "<td></td>\n"; }
      ++$n;
    }
    print "</tr>\n";
  }
  print	"</table>\n";
}


#### �ݒ�l�^�C�g�� ####
my @str_LENGTH_UNIT  = &TMSscanner::get_str_length_unit();

my $width = 800;
if( $beam_type == 2 ){ $width = 950; }

print "<div class=table-responsive>\n".	
"<table class=table table-striped border=1>\n".
	"<tr align=center bgcolor=$menu_color>\n".
  "<thead class='thead-dark' >\n".
	"<th scope=col bgcolor=#0000 nowrap><font color=white>TEAR</font></th>\n".
	"<th scope=col bgcolor=#0000 nowrap><font color=white>ARTIGO</font></th>\n".
	"<th scope=col bgcolor=#0000 nowrap><font color=white>STATUS_TEAR</font></th>\n".
	"<th scope=col bgcolor=#0000 nowrap><font color=white>DURACAO</font></th>\n".
	"<th scope=col bgcolor=#0000 nowrap><font color=white>PARADAS_TURNO_ATUAL<br>\n".
  "<th scope=col bgcolor=#0000 nowrap><font color=white>EFICIENCIA_TUNO_ATUAL<br>\n".
  "<th scope=col bgcolor=#0000 nowrap><font color=white>PARADAS_24H<br>\n".
  "<th scope=col bgcolor=#0000 nowrap><font color=white>EFCIENCIA_24H<br>\n".
	"<th scope=col bgcolor=#0000 nowrap><font color=white>$str_RPM</font></th>\n".
	"<th scope=col bgcolor=#0000 nowrap><font color=white>PREVISAO_TROCA_ROLO_TECIDO</font></th>\n".
  "<th scope=col bgcolor=#0000 nowrap><font color=white>REVISAO_TROCA_ROLO_URDUME</font></th>\n".
	"</tr>\n".
  "</thead>\n";

#### �ݒ�l�̓��� ####
for( my $i=$disp_start; $i<$disp_end; $i++ ){
  my ($mac_id, $mac_name) = @{$loom_id_name[$i]};

  if( ! exists($loom_status{$mac_id}) ){ next; }

  my ( $style,
       $status,
       $duration,
       $effic_shift,
       $effic_24h,
       $stop_shift,
       $stop_24h,
       $rpm,
       $doff_percent,
       $doff_forecast,
       $wout_percent,
       $wout_forecast,
       $ubeam_use,
       $uwout_percent,
       $uwout_forecast ) = @{$loom_status{$mac_id}};

  print "<tbody>\n".
  "<tr align=center bgcolor=$body_color>\n".
	"<th scope=row nowrap>$mac_name</th>\n";

  print "<td nowrap>$style</td>\n";
  print "<td nowrap bgcolor=$bg_color{$status}>\n".
        "<font color=$font_color{$status}>$str_status{$status}</font></td>\n";

  print "<td nowrap>".&print_duration($status,$duration)."</td>\n";

  print "<td>$stop_shift</td>\n";
  print "<td type=number>".$effic_shift."%"."</td>\n";
  print "<td>$stop_24h</td>\n";
  print "<td type=number>".$effic_24h."%"."</td>\n";
  print "<td>$rpm</td>\n";
  print "<td nowrap align=right>".&min_to_hhmm($doff_forecast)."</td>\n";  
  print "<td nowrap align=right>".&min_to_hhmm($wout_forecast)."</td>\n";
 

  if( $beam_type == 2 ){
    if( $ubeam_use == 1 ){
      print "<td nowrap align=right>".&min_to_hhmm($uwout_forecast)."</td>\n";
      print "<td nowrap align=center>".&percent_bar($uwout_percent)."</td>\n";
    }else{
      print "<td colspan=2></td>\n";
    }
  }

  print "</tr>\n".
  "</tbody>\n";
}

print	"</table>\n".
"</div>\n".
	"<BR></form>\n".

	#&TMScommon::make_footer
  (
  #  'dummy','menu', 
  #  $lang
  ).
	"</center></body></html>\n";

exit;

########################################################################

sub print_duration
{
  my ($status,$sec) = @_;

  if( $sec eq "" ){ return ""; }

  my $h = int($sec / 3600);
  my $m = int(($sec % 3600) / 60);
  my $hhmm = sprintf("%d:%02d",$h,$m);

  if( $sec >= (5*60) ){  # 5���ȏ�
    if( ($status ne 'Run'            ) and
        ($status ne 'Out_of_product' ) and
        ($status ne 'Warp_out'       ) and
        ($status ne 'Cloth_doffing'  ) and
        ($status ne 'Machine_failure') and
        ($status ne 'Cloth_mending'  ) and
        ($status ne 'Power_off'      ) ){

      return "<font color=red>$hhmm</font>";
    }
  }

  return $hhmm;
}


########################################################################

sub percent_bar
{
  my ($percent) = @_;

  if( $percent eq "" ){ return ""; }

  my $blue = int($percent); # �O�̂���
  my $gray = 100 - $blue;

  my $html = "";
  if( $blue > 0 ){
    $html .= "<IMAGE src=\"color/blue.jpg\" height=15 width=$blue align=middle>";
  }
  if( $gray > 0 ){
    $html .= "<IMAGE src=\"color/gray.jpg\" height=15 width=$gray align=middle>";
  }

  return $html;
}


########################################################################

sub min_to_hhmm
{
  my ($min) = @_;

  if( $min eq "" ){ return ""; }

  my $h = int($min / 60);
  my $m = $min % 60;

  return sprintf("%d:%02d",$h,$m);
}


########################################################################

sub get_loom_id_name_list
{

  # �X�L���i�[�̋@���o�^
  my @loom_set = &TMSscanner::get_loom_setting( "mac_name" );

  # �@�䖼�����ݒ�̏ꍇ�́A�@��ID�ŕ\��
  foreach(@loom_set){
    if( length($$_[1]) == 0 ){ $$_[1] = $$_[0]; }
  }

  # JAT710�̋@���o�^
  my @ip_list = &TMSipset::get_all_ip_list();
  if( $#ip_list >= 0 ){
    my @name_list = ();
    &TMSipset::get_name_ip_list( \@name_list, \@ip_list );
    for( my $i=0; $i<=$#name_list; $i++ ){
      push( @loom_set, [$ip_list[$i], $name_list[$i]] );
    }
  }

  return @loom_set;  # �\�[�g�͂��Ȃ�
}

########################################################################

sub make_status_data
{
  my ($ref_data,$ref_stat) = @_;

  my $style  = "";
  my $status = "";
  my $duration    = 0;
  my $effic_shift = "0.0";
  my $effic_24h   = "0.0";
  my $effic_shift_ = "0.0";
  my $effic_24h_   ="0.0";
  #my $effic_shift = 0;
  #my $effic_24h   = 0;
  my $stop_shift  = 0;
  my $stop_24h    = 0;
  my $rpm         = 0;
  my $doff_percent  = 0;
  my $doff_forecast = 0;
  my $wout_percent  = 0;
  my $wout_forecast = 0;
  my $ubeam_use      = 0;
  my $uwout_percent  = 0;
  my $uwout_forecast = 0;

  # -----------------------------------

  my $Stop            = 0;
  my $Warp_top        = 0;
  my $Warp            = 0;
  my $False_selvage   = 0;  # only JAT710
  my $CatchCode_front = 0;  # only LWT710
  my $CatchCode_rear  = 0;  # only LWT710
  my $Leno_L          = 0;
  my $Leno_R          = 0;
  my $Weft            = 0;
  my $Manual          = 0;
  my $Out_of_product  = 0;
  my $Warp_out        = 0;
  my $Cloth_doffing   = 0;
  my $Cloth_mending   = 0;
  my $Machine_failure = 0;
  my $Power_off       = 0;

  my $Stop_time = 0;
  my $Run_time  = 0;

  my $mac_type = "JAT710";  # Machine_type= ��������΁A"JAT710"

  my $scnt = 0;
  my $dcnt = 0;
  my $vcnt = 0;
  foreach my $line (@$ref_data){
    if( $line =~ m/^Machine_type=LWT710/ ){ $mac_type = "LWT710"; }

    #(State)                                                                        JAT LWT
    elsif( $line =~ m/^Stop=(.+)/            ){ $Stop            = $1; ++$scnt; }  #  1   1
    elsif( $line =~ m/^Warp_top=(.+)/        ){ $Warp_top        = $1; ++$scnt; }  #  2   2
    elsif( $line =~ m/^Warp=(.+)/            ){ $Warp            = $1; ++$scnt; }  #  3   3
    elsif( $line =~ m/^False_selvage=(.+)/   ){ $False_selvage   = $1; ++$scnt; }  #  4    
    elsif( $line =~ m/^CatchCode_front=(.+)/ ){ $CatchCode_front = $1; ++$scnt; }  #      4
    elsif( $line =~ m/^CatchCode_rear=(.+)/  ){ $CatchCode_rear  = $1; ++$scnt; }  #      5
    elsif( $line =~ m/^Leno_L=(.+)/          ){ $Leno_L          = $1; ++$scnt; }  #  5   6
    elsif( $line =~ m/^Leno_R=(.+)/          ){ $Leno_R          = $1; ++$scnt; }  #  6   7
    elsif( $line =~ m/^Weft=(.+)/            ){ $Weft            = $1; ++$scnt; }  #  7   8
    elsif( $line =~ m/^Manual=(.+)/          ){ $Manual          = $1; ++$scnt; }  #  8   9
    elsif( $line =~ m/^Out_of_product=(.+)/  ){ $Out_of_product  = $1; ++$scnt; }  #  9  10
    elsif( $line =~ m/^Warp_out=(.+)/        ){ $Warp_out        = $1; ++$scnt; }  # 10  11
    elsif( $line =~ m/^Cloth_doffing=(.+)/   ){ $Cloth_doffing   = $1; ++$scnt; }  # 11  12
    elsif( $line =~ m/^Cloth_mending=(.+)/   ){ $Cloth_mending   = $1; ++$scnt; }  # 12  13
    elsif( $line =~ m/^Machine_failure=(.+)/ ){ $Machine_failure = $1; ++$scnt; }  # 13  14
    elsif( $line =~ m/^Power_off=(.+)/       ){ $Power_off       = $1; ++$scnt; }  # 14  15

    #(Data)
    elsif( $line =~ m/^Rpm=(.+)/                   ){ $rpm            = $1; ++$dcnt; }  #  1
    elsif( $line =~ m/^Shift_efficiency=(.+)/      ){ $effic_shift    = $1; ++$dcnt; }  #  2
    elsif( $line =~ m/^24h_efficiency=(.+)/        ){ $effic_24h      = $1; ++$dcnt; }  #  3
    elsif( $line =~ m/^Shift_stops=(.+)/           ){ $stop_shift     = $1; ++$dcnt; }  #  4
    elsif( $line =~ m/^24h_stops=(.+)/             ){ $stop_24h       = $1; ++$dcnt; }  #  5
    elsif( $line =~ m/^Stop_time=(.+)/             ){ $Stop_time      = $1; ++$dcnt; }  #  6
    elsif( $line =~ m/^Run_time=(.+)/              ){ $Run_time       = $1; ++$dcnt; }  #  7
    elsif( $line =~ m/^Cloth_change_forecast=(.+)/ ){ $doff_percent   = $1; ++$dcnt; }  #  8
    elsif( $line =~ m/^Cloth_change_time=(.+)/     ){ $doff_forecast  = $1; ++$dcnt; }  #  9
    elsif( $line =~ m/^Beam_out_forecast=(.+)/     ){ $wout_percent   = $1; ++$dcnt; }  # 10
    elsif( $line =~ m/^Beam_out_time=(.+)/         ){ $wout_forecast  = $1; ++$dcnt; }  # 11
    elsif( $line =~ m/^Top_beam_out_forecast=(.+)/ ){ $uwout_percent  = $1; ++$dcnt; }  # 12
    elsif( $line =~ m/^Top_beam_out_time=(.+)/     ){ $uwout_forecast = $1; ++$dcnt; }  # 13

    #(Set Value)
    elsif( $line =~ m/^Style_name=(.+)/   ){ $style     = $1; ++$vcnt; }  # 1
    elsif( $line =~ m/^Top_beam_use=(.+)/ ){ $ubeam_use = $1; ++$vcnt; }  # 2
  }

  # �f�[�^�����`�F�b�N
  if( $mac_type eq "JAT710" ){
    if( $scnt < 14 ){ return 1; } # ERROR
  }else{ # LWT710
    if( $scnt < 15 ){ return 1; } # ERROR
  }
  if( ($dcnt < 13) or ($vcnt < 2) ){
    return 1;  # ERROR
  }

  $style =~ s/^"//;  # �擪�ƁA�Ō�� " ������
  $style =~ s/"$//;  # 

  # ---------------------------------------------------------

  if( $Stop == 0 ){ $status = "Run"; }
  else{
    $status = "Other";
    if( $Manual          == 1 ){ $status = "Manual";          }
    if( $Weft            == 1 ){ $status = "Weft";            }
    if( $Leno_R          == 1 ){ $status = "Leno_R";          }
    if( $Leno_L          == 1 ){ $status = "Leno_L";          }
    if( $CatchCode_rear  == 1 ){ $status = "CatchCode_rear";  }
    if( $CatchCode_front == 1 ){ $status = "CatchCode_front"; }
    if( $False_selvage   == 1 ){ $status = "False_selvage";   }
    if( $Warp            == 1 ){ $status = "Warp";            }
    if( $Warp_top        == 1 ){ $status = "Warp_top";        }
    if( $Power_off       == 1 ){ $status = "Power_off";       }
    if( $Cloth_mending   == 1 ){ $status = "Cloth_mending";   }
    if( $Machine_failure == 1 ){ $status = "Machine_failure"; }
    if( $Cloth_doffing   == 1 ){ $status = "Cloth_doffing";   }
    if( $Warp_out        == 1 ){ $status = "Warp_out";        }
    if( $Out_of_product  == 1 ){ $status = "Out_of_product";  }
  }

  if( $Stop == 1 ){ $duration = $Stop_time; }
  else{             $duration = $Run_time; }

  # "100.0" -> "100" �ɂ���
  if( $effic_shift >= 100 ){ $effic_shift = "100"; }
  if( $effic_24h   >= 100 ){ $effic_24h   = "100"; }

  @$ref_stat = ($style,           #  1
                $status,          #  2
                $duration,        #  3
                $effic_shift,     #  4
                $effic_24h,       #  5
                $stop_shift,      #  6
                $stop_24h,        #  7
                $rpm,             #  8
                $doff_percent,    #  9
                $doff_forecast,   # 10
                $wout_percent,    # 11
                $wout_forecast,   # 12
                $ubeam_use,       # 13
                $uwout_percent,   # 14
                $uwout_forecast); # 15

  return 0; # OK
}

#$effic_shift_ = str_replace($effic_shift,'.',',');
#$effic_shift = $effic_shift_;



## -------------------------------------------------------------------------

#### httpc.exe �̃G���[�ԍ�(100-999) #####

use constant ERR__PING_TIMEOUT    => 100;
use constant ERR__ARG_ERROR       => 200;
use constant ERR__BAD_HOST_NAME   => 201;
use constant ERR__POST_FILE_ERROR => 210;
use constant ERR__HTTP_NOT_FOUND  => 220;
use constant ERR__HTTP_ERROR      => 300;
use constant ERR__SOCKET_ERROR    => 400;
use constant ERR__PING_ERROR      => 410;
use constant ERR__SYSTEM_ERROR    => 900;

#### opestate.cgi �Ǝ��̃G���[�ԍ� ########

use constant ERR__NOT_SUPPORT     => 1000;
use constant ERR__DATA_ERROR      => 1001;

###########################################

sub make_error_status
{
  my ($err) = @_;

             #  1  2  3  4  5  6  7  8  9 10 11 12 13 14 15
  my @state = ("","","","","","","","","","","","","","","");

  if(    $err == ERR__PING_TIMEOUT   ){ $state[1] = "Power_off";    }
  elsif( $err == ERR__PING_ERROR     ){ $state[1] = "Comm_error";   }
  elsif( $err == ERR__SOCKET_ERROR   ){ $state[1] = "Comm_error";   }
  elsif( $err == ERR__HTTP_ERROR     ){ $state[1] = "Comm_error";   }
  elsif( $err == ERR__HTTP_NOT_FOUND ){ $state[1] = "Comm_error";   }
  elsif( $err == ERR__NOT_SUPPORT    ){ $state[1] = "Not_support";  }
  elsif( $err == ERR__DATA_ERROR     ){ $state[1] = "Data_error";   }
  else{                                 $state[1] = "System_error"; }

  return @state;
}

## -------------------------------------------------------------------------

sub get_scan_loom_status
{
  my ( $scan_ip, $r_mac_id, $r_state ) = @_;

  # �t�@�C����؂蕶����( �p���� . * - _ �̂ݎg�p�B�X�y�[�X�s��)

  my $boundary_str = "----------mget-boundary-strings----------";


  #### POST�f�[�^ ���ꎞ�t�@�C���ɏ������� ####

  my $err = ERR__SYSTEM_ERROR;  # �f�t�H���g�̃G���[

  my $post_file = &TMScommon::get_tmp_file_name("stat_post");
  if( open(FILE,"> $post_file") ){
    binmode(FILE);  # �o�C�i���[���[�h�ɂ���

    print FILE "boundary=".$boundary_str;

    # ��ŁA�t�@�C��������@�䖼���t�����ł���l�ɁA�A�z�z�������Ă���
    my %file2mac_id = ();

    foreach my $mac_id ( @$r_mac_id ){
      if( $mac_id =~ m/S([1-5])-([0-9]+)\.([0-9]+)/ ){
        my $filename = sprintf("..\\data\\status\\%02d%03d.txt",$2,$3); # cgi-bin ����̑��΃p�X
        print FILE "&file=$filename";

        $file2mac_id{$filename} = $mac_id;
      }
    }
    close(FILE);

    #### �f�[�^���擾���� ####

    # (�Q�l)�R�}���h���C���������� 2047����(NT,2000) 8191����(XP) �܂�OK
    if( open(PIPE,"..\\bin\\httpc.exe \"$scan_ip\" \"/TmsScanner/cgi-bin/mget.cgi\" \"\" $post_file |") ){
      my @data = <PIPE>;
      close(PIPE);

      if( $? != 0 ){  # httpc.exe ���s
        if( defined($data[0]) ){
          if( $data[0] =~ m/^(\d{3})\s/ ){  # �擪���R���̐����Ȃ�
            $err = int($1);
          }
        }
      }
      else{  # httpc.exe ����

        my @each_data;  # �P�䖈�̃f�[�^
        my $boundary_level = 0;
        my $mac_id = "";

        foreach(@data){
          chomp;
          if( $boundary_level == 1 ){  # ��؂蕶���̒���̍s�A�t�@�C����
            if( exists($file2mac_id{$_}) ){
              $mac_id = $file2mac_id{$_};
              $boundary_level = 2;
              @each_data = ();
            }else{
              $mac_id = "";
              $boundary_level = 0;
            }
          }
          elsif( $boundary_level == 2 ){  # �f�[�^�s
            if( $_ eq $boundary_str ){
              if( $#each_data >= 0 ){
                if( length($each_data[$#each_data]) == 0 ){  # �Ō�̍s��0�����Ȃ�
                  $#each_data = $#each_data -1;  # �Ō�̍s���폜(��؂蕶���̈ꕔ�Ȃ̂�)
                }
              }
              $boundary_level = 1;
              my @stat = ();
              if( 0 == &make_status_data(\@each_data,\@stat) ){
                @{${$r_state}{$mac_id}} = @stat;
              }else{
                @{${$r_state}{$mac_id}} = &make_error_status(ERR__DATA_ERROR);
              }
            }else{
              push(@each_data, $_);  # �f�[�^�̎�荞��
            }
          }else{
            if( $_ eq $boundary_str ){
              $boundary_level = 1;
            }
          }
        }
      }
    }

    unlink($post_file);  # �ꎞ�t�@�C�����폜
  }

  # �f�[�^���擾�ł��Ȃ��@��̃G���[�X�e�[�^�X

  foreach my $mac_id ( @$r_mac_id ){
    if( ! exists(${$r_state}{$mac_id}) ){
      @{${$r_state}{$mac_id}} = &make_error_status($err);
    }
  }

}


###################################################################################################


## �����ڑ��� ##
use constant PIPE_MAX => 5;


sub get_jat710_loom_status
{
  my ( $r_ip_addr, $r_state ) = @_;

  my $path = "/cgi-bin/ext.cgi?func=get_stat";

  my @get_list = ();  # �����Ɏ擾����Ώۂ̃��X�g�i�Q�d�z��j

  # ---- �P��ڂ̃f�[�^�擾���� ----

  my $ip_pos = 0;
  while( ($ip_pos < PIPE_MAX) and ($ip_pos <= $#{$r_ip_addr}) ){

    my $ip = ${$r_ip_addr}[$ip_pos];
    $ip_pos++;

    my $num = sprintf("%02d",$ip_pos);
    my $pipe = "PIPE$num";
    my $tmpfile = &TMScommon::get_tmp_file_name("opest$num");

    # (�Q�l)�R�}���h���C���������� 2047����(NT,2000) 8191����(XP) �܂�OK
    if( open($pipe,"..\\bin\\httpc.exe \"$ip\" \"$path\" > \"$tmpfile\" |") ){
      push(@get_list,[$ip,$pipe,$tmpfile]);
    }
  }

  # ---- httpc.exe �̏I����҂��A���ʂ����ɏ������Ă��� ----

  while( $#get_list >= 0 ){

    my @next_list = ();  # ���̃f�[�^�擾�p

    for( my $i=0; $i<=$#get_list; $i++ ){

      my ($ip,$pipe,$tmpfile) = @{$get_list[$i]};

      my $dummy = <$pipe>;  # httpc.exe �̏I����҂�
      close($pipe);

      # ---- �擾�����f�[�^�̏��� ----
      my $err = ERR__SYSTEM_ERROR;

      if( $? == 0 ){  # httpc.exe ����
        if( open(FILE,"< $tmpfile") ){
          my @data = ();
          while(<FILE>){  # �f�[�^�ǂݍ���
            chomp;
            push(@data,$_);
          }
          close(FILE);

          if( $#data < 0 ){ $err = ERR__DATA_ERROR; }
          else{
            if( ($data[0] =~ m/^Not supported\./) or
                ($data[0] =~ m/^func\(command\) not found\./) or
                ($#data == 19) ){  # 20�s�́A���d�l
              $err = ERR__NOT_SUPPORT;
            }
            else{
              my @stat = ();
              if( 0 == &make_status_data(\@data,\@stat) ){
                @{${$r_state}{$ip}} = @stat;
                $err = 0;
              }else{
                $err = ERR__DATA_ERROR;
              }
            }
          }
        }
      }
      else{  # httpc.exe ���s
        if( open(FILE, "< $tmpfile") ){  # �ꎞ�t�@�C�����J��
          my $line = <FILE>;  # �P�s�ړǂݍ���
          close(FILE);

          if( defined($line) ){
            if( $line =~ m/^(\d{3})\s/ ){  # �擪���R���̐����Ȃ�
              $err = int($1);
            }
          }
        }
      }

      unlink($tmpfile);  # �ꎞ�t�@�C��������

      # �G���[���̃X�e�[�^�X�擾
      if( $err != 0 ){
        @{${$r_state}{$ip}} = &make_error_status($err);
      }

      # ---- ���̃f�[�^�擾�������n�߂� ----
      if( $ip_pos <= $#{$r_ip_addr} ){
        $ip = ${$r_ip_addr}[$ip_pos];  # ���̑Ώۋ@��
        $ip_pos++;

        # (�Q�l)�R�}���h���C���������� 2047����(NT,2000) 8191����(XP) �܂�OK
        if( open($pipe,"..\\bin\\httpc.exe \"$ip\" \"$path\" > \"$tmpfile\" |") ){
          push(@next_list,[$ip,$pipe,$tmpfile]);
        }
      }
    }

    @get_list = @next_list;
  }
}


