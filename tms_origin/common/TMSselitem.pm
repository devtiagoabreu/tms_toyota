package TMSselitem;

###################################################################################################
#
#  TMSselitem.pm
#
###################################################################################################

use strict;

use TMScommon;

###################################################################################################
# 初期値

my @item2 = (	0,	# Top Beam
		0,	# Beam
		1,	# RPM
		1,	# Efficiency
		1,	# Run Time
		1,	# Stop Time
		1  );	# Production

my @item = (	0,	# Warp top miss
		1,	# Warp miss
		0,	# False selvage miss
		0,	# Leno(L) miss
		0,	# Leno(R) miss
		1,	# Weft
		0,	# Warp out
		0,	# Cloth doffing
		0,	# Manual stop
		0,	# Other
		0  );	# Power off

my @item3 = (	0,	# CC Front  # add 2006.11.15
		0,	# CC Rear
		0  );	# Leno Total

my @detail = (	0,	# WF1
		0,	# WF2
		0  );	# LH

my @color = (	0,	# Color1
		0,	# Color2
		0,	# Color3
		0,	# Color4
		0,	# Color5
		0  );	# Color6 

my $beam_type = 1;
my $unit      = 0;
my $period    = 'shift';
my $week      = 0;
my $effic     = 0;
my $run_tm    = 0;
my $expire    = 26;  # 26時間 add 2006.11.15

#　設定値ファイルから読み出し

if( open(SELITEM,'< ../../tmsdata/setting/selitem.txt') ){
  while(<SELITEM>){
    $_ =~ s/\n$//;		# 改行コードを削除。
    $_ =~ s/\s+/ /g;		# ２個以上のスペースを１個にする。
    my @data = split(/ /);
    if( $#data >= 1 ){
      my $key = shift @data;
      if(    $key eq "item2" ){
	if( $#data > $#item2 ){ $#data = $#item2; }
	for( my $i=0; $i<=$#data; $i++ ){ $item2[$i] = $data[$i]; }
      }
      elsif( $key eq "item" ){
	if( $#data > $#item ){ $#data = $#item; }
	for( my $i=0; $i<=$#data; $i++ ){ $item[$i] = $data[$i]; }
      }
      elsif( $key eq "item3" ){
	if( $#data > $#item3 ){ $#data = $#item3; }
	for( my $i=0; $i<=$#data; $i++ ){ $item3[$i] = $data[$i]; }
      }
      elsif( $key eq "detail" ){
	if( $#data > $#detail ){ $#data = $#detail; }
	for( my $i=0; $i<=$#data; $i++ ){ $detail[$i] = $data[$i]; }
      }
      elsif( $key eq "color" ){
	if( $#data > $#color ){ $#data = $#color; }
	for( my $i=0; $i<=$#data; $i++ ){ $color[$i] = $data[$i]; }
      }
      elsif( $key eq "beam_type" ){ $beam_type = $data[0]; }
      elsif( $key eq "unit"      ){ $unit      = $data[0]; }
      elsif( $key eq "period"    ){ $period    = $data[0]; }
      elsif( $key eq "week"      ){ $week      = $data[0]; }
      elsif( $key eq "effic"     ){ $effic     = $data[0]; }
      elsif( $key eq "run_tm"    ){ $run_tm    = $data[0]; }
      elsif( $key eq "expire"    ){ $expire    = $data[0]; }
    }
  }
  close(SELITEM);
}

## 対象機台の仕様ファイルから読み出し

my $jat_ari = 1;  # true
my $lwt_ari = 1;  # true

if( open(FILE,'< ../setting/mac_type.txt') ){
  while(<FILE>){
    $_ =~ s/\n$//;	# 改行コードを削除。
    $_ =~ s/\s+/ /g;	# ２個以上のスペースを１個にする。

    if( $_ eq "JAT nashi" ){ $jat_ari = 0; } # false
    if( $_ eq "LWT nashi" ){ $lwt_ari = 0; } # false
  }
  close(FILE);
}

## 対象機台に合わせて、設定を変更

if( $jat_ari == 0 ){
  $color[3]  = 0; # Color4
  $color[4]  = 0; # Color5
  $color[5]  = 0; # Color6
}
if( $lwt_ari == 0 ){
  $item3[0] = 0;  # CC front
  $item3[1] = 0;  # CC back
}


#----------------------------------------------------

sub is_jat_ari { return $jat_ari; }
sub is_lwt_ari { return $lwt_ari; }

sub save_mac_type
{
  my ($jat_val, $lwt_val) = @_;

  # 両方無しは、設定保存しない
  if( ($jat_val eq "nashi") and ($lwt_val eq "nashi") ){
    return;
  }

  if( open(FILE,'> ../setting/mac_type.txt') ){

    print FILE "JAT $jat_val\n".
               "LWT $lwt_val\n";

    close(FILE);
  }
}

###################################################################################################

sub save_selitem_val
{
  my ($r_item2,$r_item,$r_item3,$r_detail,$r_color,
      $v_beam_type, $v_unit,$v_period,$v_week,$v_effic,$v_run_tm,$v_expire) = @_;

  # 内部設定値を更新
  @item2     = @$r_item2;
  @item      = @$r_item;
  @item3     = @$r_item3;
  @detail    = @$r_detail;
  @color     = @$r_color;
  $beam_type = $v_beam_type;
  $unit      = $v_unit;
  $period    = $v_period;
  $week      = $v_week;
  $effic     = $v_effic;
  $run_tm    = $v_run_tm;
  $expire    = $v_expire;

  &TMScommon::make_dir('../../tmsdata');
  &TMScommon::make_dir('../../tmsdata/setting');

  # ファイルにセーブ
  open(SELITEM, '> ../../tmsdata/setting/selitem.txt');

  print SELITEM "Version 3.00\n";

  print SELITEM "item2    ";
  foreach( @item2  ){ print SELITEM " $_"; }
  print SELITEM "\n";

  print SELITEM "item     ";
  foreach( @item   ){ print SELITEM " $_"; }
  print SELITEM "\n";

  print SELITEM "item3    ";
  foreach( @item3  ){ print SELITEM " $_"; }
  print SELITEM "\n";

  print SELITEM "detail   ";
  foreach( @detail ){ print SELITEM " $_"; }
  print SELITEM "\n";

  print SELITEM "color    ";
  foreach( @color  ){ print SELITEM " $_"; }
  print SELITEM "\n";

  print SELITEM "beam_type $beam_type\n".
  		"unit      $unit\n".
		"period    $period\n".
		"week      $week\n".
		"effic     $effic\n".
		"run_tm    $run_tm\n".
		"expire    $expire\n";

  close(SELITEM);
}

###################################################################################################

sub get_value_of_item2
{
  return @item2;  # レポート項目
}

sub get_value_of_item
{
  return @item;   # 停止原因
}

sub get_value_of_item3
{
  return @item3;   # 停止原因（LWT対応での追加分）
}

sub get_value_of_detail
{
  return @detail;
}

sub get_value_of_color
{
  return @color;
}

sub get_value_of_beam_type
{
  return $beam_type;
}

sub get_value_of_unit
{
  return $unit;
}

sub get_value_of_beam_unit
{
  if( $unit == 2 ){ return 1; }	# yard        -> yard
  return 0;			# pick, meter -> meter
}

sub get_value_of_period
{
  return $period;
}

sub get_value_of_week
{
  return $week;
}

sub get_value_of_effic
{
  return $effic;
}

sub get_value_of_run_tm
{
  return $run_tm;
}

sub get_value_of_expire
{
  return $expire;
}

###################################################################################################
# for Setting Page

sub get_key_of_item2
{
  return (	'top_beam',
  		'beam',
		'rpm',
		'effic',
		'run',
		'stop',
		'product'	);
}

sub get_key_of_item
{
  return (	'warp_top',
		'warp',
		'false',
		'leno_l',
		'leno_r',
		'weft',
		'warp_out',
		'doffing',
		'manual',
		'power_off',
		'other'		);
}

sub get_key_of_item3
{
  return (	'cc_front',
		'cc_rear',
		'leno'	);
}

sub get_key_of_detail
{
  return (	'wf1',
		'wf2',
		'lh',		);
}

sub get_key_of_color
{
  return ( 1, 2, 3, 4, 5, 6 );
}

sub get_key_of_beam_type
{
  return ( 1, 2 );				# key と言うより、値のリスト
}

sub get_key_of_unit
{
  return ( 0, 1, 2 );				# key と言うより、値のリスト
}

sub get_key_of_period
{
  return ( 'shift','date','week','month' );	# key と言うより、値のリスト
}

sub get_key_of_week
{
  return ( 0, 1, 2, 3, 4, 5, 6 );		# key と言うより、値のリスト
}


###################################################################################################
# for Setting Page

sub get_menu_of_item2
{
  return ( &TMSstr::get_str( "TOP_BEAM_NAME" ),
           &TMSstr::get_str( "BEAM_NAME"     ),
           &TMSstr::get_str( "RPM"           ),
           &TMSstr::get_str( "EFFICIENCY"    ),
           &TMSstr::get_str( "RUN_TIME"      ),
           &TMSstr::get_str( "STOP_TIME"     ),
           &TMSstr::get_str( "PRODUCTION"    ) );
}

sub get_menu_of_item
{
  return ( &TMSstr::get_str( "WARP_TOP_MISS"      ),
           &TMSstr::get_str( "WARP_MISS"          ),
           &TMSstr::get_str( "FALSE_SELVAGE_MISS" ),
           &TMSstr::get_str( "LENO_L_MISS"        ),
           &TMSstr::get_str( "LENO_R_MISS"        ),
           &TMSstr::get_str( "WEFT_MISS"          ),
           &TMSstr::get_str( "WARP_OUT"           ),
           &TMSstr::get_str( "CLOTH_DOFFING"      ),
           &TMSstr::get_str( "MANUAL_STOP"        ),
           &TMSstr::get_str( "POWER_OFF"          ),
           &TMSstr::get_str( "OTHER_STOP"         ) );
}

sub get_menu_of_item3
{
  return ( &TMSstr::get_str( "CC_FRONT_MISS" ),
           &TMSstr::get_str( "CC_REAR_MISS"  ),
           &TMSstr::get_str( "LENO_MISS"     ) );
}

sub get_menu_of_detail
{
  return ( &TMSstr::get_str( "WF1" ),
           &TMSstr::get_str( "WF2" ),
           &TMSstr::get_str( "LH"  ) );
}

sub get_menu_of_color
{
  return ( &TMSstr::get_str( "COLOR1" ),
           &TMSstr::get_str( "COLOR2" ),
           &TMSstr::get_str( "COLOR3" ),
           &TMSstr::get_str( "COLOR4" ),
           &TMSstr::get_str( "COLOR5" ),
           &TMSstr::get_str( "COLOR6" ) );
}

sub get_menu_of_beam_type
{
  return ( &TMSstr::get_str( "SINGLE_BEAM" ),
           &TMSstr::get_str( "DOUBLE_BEAM" ) );
}

sub get_menu_of_unit
{
  return ( &TMSstr::get_str( "PICK"  ),
           &TMSstr::get_str( "METER" ),
           &TMSstr::get_str( "YARD"  ) );
}

sub get_menu_of_period
{
  return ( &TMSstr::get_str( "SHIFT" ),
           &TMSstr::get_str( "DATE"  ),
           &TMSstr::get_str( "WEEK"  ),
           &TMSstr::get_str( "MONTH" ) );
}

sub get_menu_of_week
{
  return ( &TMSstr::get_str( "SUNDAY"    ),
           &TMSstr::get_str( "MONDAY"    ),
           &TMSstr::get_str( "TUESDAY"   ),
           &TMSstr::get_str( "WEDNESDAY" ),
           &TMSstr::get_str( "THURSDAY"  ),
           &TMSstr::get_str( "FRIDAY"    ),
           &TMSstr::get_str( "SATDAY"    ) );
}

###################################################################################################
# for Report & Graph CSV Data Title


sub get_title_of_item2
{
  return (	'TOP_BEAM',
		'BEAM',
		'RPM',
		'EFFIC&PERCENT',
		'RUN&MINUTE',
		'STOP&MINUTE',
		'PRODUCT'	);
}

sub get_title_of_item
{
  return (	'WARP_TOP',
		'WARP',
		'FALS',
		'LENO_L',
		'LENO_R',
		'WEFT',
		'WARP_OUT',
		'DOFF',
		'MANUAL',
		'PWR_OFF',
		'OTHER'		);
}

sub get_title_of_item3
{
  return (	'CC_FRONT',
		'CC_REAR',
		'LENO'		);
}

sub get_title_of_detail
{
  return (	'WF1',
		'WF2',
		'LH'		);
}

sub get_title_of_color
{
  return (	'COLOR1',
		'COLOR2',
		'COLOR3',
		'COLOR4',
		'COLOR5',
		'COLOR6'	);
}

sub get_title_of_unit
{
  if( $unit == 2 ){ return 'YARD';  }
  if( $unit == 1 ){ return 'METER'; }
  return 'PICK';
}

sub get_title_of_beam_unit
{
  if( $unit == 2 ){ return 'YARD';  }	# yard        -> yard
  return 'METER';			# pick, meter -> meter
}

###################################################################################################
1;
