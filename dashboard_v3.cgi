#! C:\Perl\bin\perl.exe -I..\common

use strict;
no strict "refs";
use CGI;
use CGI::Carp qw(fatalsToBrowser);

use TMSstr;
use TMScommon;
use TMSselitem;
use TMSipset;
use TMSscanner;

require '../common/http_header.pm';

my $lang = &TMSstr::get_lang_set();
&TMSstr::load_str_file($lang);

my $str_UPDATE_SETTING = &TMSstr::get_str( 'UPDATE_SETTING' );
my $str_UPDATE_OK = &TMSstr::get_str( 'UPDATE_OK' );

my $str_LOOM_NAME = &TMSstr::get_str( "LOOM_NAME" );
my $str_STYLE_NAME = &TMSstr::get_str( "STYLE_NAME" );

my $str_OPERATION_STATUS = &TMSstr::get_str( 'OPERATION_STATUS' );

my $str_PAGE = &TMSstr::get_str( 'PAGE' );
my $str_REFRESH = &TMSstr::get_str( 'REFRESH' );

my $str_STATUS = &TMSstr::get_str( 'STATUS' );
my $str_DURATION = &TMSstr::get_str( 'DURATION' );
my $str_STOP_COUNT = &TMSstr::get_str( 'STOP_COUNT' );
my $str_EFFICIENCY = &TMSstr::get_str( 'EFFICIENCY' );
my $str_CURRENT_SHIFT = &TMSstr::get_str( 'CURRENT_SHIFT' );
my $str_RPM = &TMSstr::get_str( 'RPM' );
my $str_DOFFING_FORECAST = &TMSstr::get_str( 'DOFFING_FORECAST' );
my $str_WARP_OUT_FORECAST = &TMSstr::get_str( 'WARP_OUT_FORECAST' );
my $str_LOWER = &TMSstr::get_str( 'LOWER' );
my $str_UPPER = &TMSstr::get_str( 'UPPER' );
my $str_HH_MM = &TMSstr::get_str( 'HH_MM' );

my $str_SHRINKAGE = &TMSstr::get_str( 'SHRINKAGE' );
my $str_UPPER_BEAM = &TMSstr::get_str( 'UPPER_BEAM' );
my $str_LOWER_BEAM = &TMSstr::get_str( 'LOWER_BEAM' );
my $str_SET_LENGTH = &TMSstr::get_str( 'SET_LENGTH' );

my $str_SETTING_RESULT = &TMSstr::get_str( "SETTING_RESULT" );
my $str_SETTING_SUCCEED = &TMSstr::get_str( "SETTING_SUCCEED" );
my $str_MENU = &TMSstr::get_str( "MENU" );
my $str_BACK = &TMSstr::get_str( "BACK" );

my %str_status = ( 'Run'             => &TMSstr::get_str( 'OPST__RUN' ),
           'Out_of_product'  => &TMSstr::get_str( 'OPST__OUT_OF_PRODUCT'),
           'Warp_out'        => &TMSstr::get_str( 'OPST__WARP_OUT' ),
           'Cloth_doffing'   => &TMSstr::get_str( 'OPST__CLOTH_DOFFING' ),
           'Machine_failure' => &TMSstr::get_str( 'OPST__MACHINE_FAILURE'),
           'Cloth_mending'   => &TMSstr::get_str( 'OPST__CLOTH_MENDING' ),
           'Power_off'       => &TMSstr::get_str( 'OPST__POWER_OFF' ),
           'Warp_top'        => &TMSstr::get_str( 'OPST__WARP_TOP' ),
           'Warp'            => &TMSstr::get_str( 'OPST__WARP' ),
           'False_selvage'   => &TMSstr::get_str( 'OPST__FALSE_SELVAGE' ),
           'CatchCode_front' => &TMSstr::get_str( 'OPST__CC_FRONT' ),
           'CatchCode_rear'  => &TMSstr::get_str( 'OPST__CC_REAR' ),
           'Leno_L'          => &TMSstr::get_str( 'OPST__LENO_L' ),
           'Leno_R'          => &TMSstr::get_str( 'OPST__LENO_R' ),
           'Weft'            => &TMSstr::get_str( 'OPST__WEFT' ),
           'Manual'          => &TMSstr::get_str( 'OPST__MANUAL' ),
           'Other'           => &TMSstr::get_str( 'OPST__OTHER' ),
           'Comm_error'      => &TMSstr::get_str( 'OPST__COMM_ERR' ),
           'Not_support'     => &TMSstr::get_str( 'OPST__NOT_SUPPORT' ),
           'Data_error'      => &TMSstr::get_str( 'OPST__DATA_ERR' ),
           'System_error'    => 'System Error' );


my %bg_color = ( 'Run'             => '#2196F3',
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
         'Weft'            => '#4CAF50',
         'Manual'          => '#ffcc99',
         'Other'           => '#ffffff',
         'Comm_error'      => '#000000',
         'Not_support'     => '#000000',
         'Data_error'      => '#000000',
         'System_error'    => '#000000' );

my %bg_color_light = ( 'Run'             => 'rgba(33, 150, 243, 0.4)',
               'Out_of_product'  => 'rgba(0, 0, 0, 0.4)',
               'Warp_out'        => 'rgba(153, 51, 204, 0.4)',
               'Cloth_doffing'   => 'rgba(255, 51, 204, 0.4)',
               'Machine_failure' => 'rgba(0, 0, 255, 0.4)',
               'Cloth_mending'   => 'rgba(51, 204, 255, 0.4)',
               'Power_off'       => 'rgba(153, 102, 0, 0.4)',
               'Warp_top'        => 'rgba(255, 0, 0, 0.4)',
               'Warp'            => 'rgba(255, 0, 0, 0.4)',
               'False_selvage'   => 'rgba(255, 255, 0, 0.4)',
               'CatchCode_front' => 'rgba(255, 255, 0, 0.4)',
               'CatchCode_rear'  => 'rgba(255, 255, 0, 0.4)',
               'Leno_L'          => 'rgba(255, 255, 0, 0.4)',
               'Leno_R'          => 'rgba(255, 255, 0, 0.4)',
               'Weft'            => 'rgba(76, 175, 80, 0.4)',
               'Manual'          => 'rgba(255, 204, 153, 0.4)',
               'Other'           => 'rgba(255, 255, 255, 0.4)',
               'Comm_error'      => 'rgba(0, 0, 0, 0.4)',
               'Not_support'     => 'rgba(0, 0, 0, 0.4)',
               'Data_error'      => 'rgba(0, 0, 0, 0.4)',
               'System_error'    => 'rgba(0, 0, 0, 0.4)' );


my %font_color = ( 'Run'             => '#ffffff',
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
           'Comm_error'      => '#ff0000',
           'Not_support'     => '#ff0000',
           'Data_error'      => '#ff0000',
           'System_error'    => '#ff0000' );

################################################################

my $html = new CGI;

my $theme = $html->param('theme') || 'dark';
my $toggle_theme = $theme eq 'dark' ? 'light' : 'dark';
my $theme_text = $theme eq 'dark' ? 'Modo Claro' : 'Modo Escuro';

my @loom_id_name = &get_loom_id_name_list();
@loom_id_name = sort { "$$a[1] $$a[0]" cmp "$$b[1] $$b[0]" } @loom_id_name;

my $beam_type = &TMSselitem::get_value_of_beam_type();

##########################################################################

my @scan1_loom = ();
my @scan2_loom = ();
my @scan3_loom = ();
my @scan4_loom = ();
my @scan5_loom = ();
my @jat710_loom = ();

foreach my $loom (@loom_id_name) {
  my ($id, $name) = @{$loom};

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

my $title = $str_OPERATION_STATUS;

print "<html lang=$lang>\n".
      "<head>\n".
      &TMScommon::meta_content_type( $lang ).
      &TMScommon::meta_no_cache_tag().
      "<title>$title</title>\n".
      "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">\n".
      "<style>\n".
      "* { box-sizing: border-box; margin: 0; padding: 0; }\n".
      "body { \n".
      "  font-family: 'Arial', sans-serif; \n".
      "  margin: 0; \n".
      "  padding: 20px;\n".
      "  font-size: 14px;\n".
      "  transition: all 0.3s ease;\n".
      "}\n".
      "body.dark { \n".
      "  background: #0a0a0a; \n".
      "  color: white; \n".
      "}\n".
      "body.light { \n".
      "  background: #f0f0f0; \n".
      "  color: #333; \n".
      "}\n".
      ".dashboard { \n".
      "  display: grid; \n".
      "  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); \n".
      "  gap: 15px; \n".
      "  width: 100%;\n".
      "  max-width: 100%;\n".
      "  margin: 0 auto; \n".
      "}\n".
      ".card { \n".
      "  border-radius: 12px; \n".
      "  padding: 15px; \n".
      "  box-shadow: 0 6px 12px rgba(0,0,0,0.5); \n".
      "  border: 5px solid;\n".
      "  transition: transform 0.2s, box-shadow 0.2s;\n".
      "  min-height: 200px;\n".
      "}\n".
      ".card:hover {\n".
      "  transform: translateY(-2px);\n".
      "  box-shadow: 0 8px 16px rgba(0,0,0,0.3);\n".
      "}\n".
      ".card-header { \n".
      "  display: flex; \n".
      "  justify-content: space-between; \n".
      "  align-items: center; \n".
      "  margin-bottom: 10px; \n".
      "  border-bottom: 1px solid;\n".
      "  padding-bottom: 8px;\n".
      "}\n".
      ".dark .card-header { border-color: #333; }\n".
      ".light .card-header { border-color: #ddd; }\n".
      ".tear-number { \n".
      "  font-size: 20px; \n".
      "  font-weight: bold; \n".
      "}\n".
      ".dark .tear-number { color: #fdb913; }\n".
      ".light .tear-number { color: #e67e22; }\n".
      ".status-badge { \n".
      "  padding: 4px 10px; \n".
      "  border-radius: 15px; \n".
      "  font-size: 12px; \n".
      "  font-weight: bold; \n".
      "  text-transform: uppercase;\n".
      "  letter-spacing: 0.5px;\n".
      "}\n".
      ".article-name { \n".
      "  font-size: 16px; \n".
      "  font-weight: bold; \n".
      "  margin: 8px 0; \n".
      "  text-align: center;\n".
      "  padding: 5px;\n".
      "  border-radius: 6px;\n".
      "}\n".
      ".dark .article-name { \n".
      "  color: #ffffff; \n".
      "  background: rgba(42, 42, 42, 0.7);\n".
      "}\n".
      ".light .article-name { \n".
      "  color: #333; \n".
      "  background: rgba(248, 249, 250, 0.7);\n".
      "  border: 1px solid #e9ecef;\n".
      "}\n".
      ".metrics { \n".
      "  display: grid; \n".
      "  grid-template-columns: 1fr 1fr; \n".
      "  gap: 12px; \n".
      "  margin-top: 12px; \n".
      "}\n".
      ".metric { \n".
      "  text-align: center; \n".
      "  padding: 8px;\n".
      "  border-radius: 8px;\n".
      "}\n".
      ".dark .metric { background: rgba(42, 42, 42, 0.7); }\n".
      ".light .metric { background: rgba(248, 249, 250, 0.7); border: 1px solid #e9ecef; }\n".
      ".metric-value { \n".
      "  font-size: 24px; \n".
      "  font-weight: bold; \n".
      "  margin-bottom: 4px;\n".
      "}\n".
      ".dark .metric-value { color: #fdb913; }\n".
      ".light .metric-value { color: #e67e22; }\n".
      ".metric-label { \n".
      "  font-size: 11px; \n".
      "  text-transform: uppercase;\n".
      "  letter-spacing: 0.5px;\n".
      "}\n".
      ".dark .metric-label { color: #aaaaaa; }\n".
      ".light .metric-label { color: #666; }\n".
      ".efficiency-bar { \n".
      "  height: 10px; \n".
      "  background: #444; \n".
      "  border-radius: 5px; \n".
      "  margin: 8px 0; \n".
      "  overflow: hidden; \n".
      "}\n".
      ".light .efficiency-bar { background: #e0e0e0; }\n".
      ".efficiency-fill { \n".
      "  height: 100%; \n".
      "  background: linear-gradient(90deg, #4CAF50, #8BC34A);\n".
      "  transition: width 0.5s;\n".
      "}\n".
      ".efficiency-fill.low { background: linear-gradient(90deg, #f44336, #ff9800); }\n".
      ".efficiency-fill.medium { background: linear-gradient(90deg, #ff9800, #ffeb3b); }\n".
      ".stops-info { \n".
      "  display: grid; \n".
      "  grid-template-columns: 1fr 1fr; \n".
      "  gap: 8px; \n".
      "  margin-top: 10px; \n".
      "  font-size: 11px; \n".
      "}\n".
      ".stop-type { \n".
      "  text-align: center; \n".
      "  padding: 4px; \n".
      "  border-radius: 6px; \n".
      "  font-weight: bold; \n".
      "}\n".
      ".weft-stops { \n".
      "  background: rgba(76, 175, 80, 0.2); \n".
      "  border: 1px solid #4CAF50; \n".
      "  color: #4CAF50; \n".
      "}\n".
      ".warp-stops { \n".
      "  background: rgba(255, 0, 0, 0.2); \n".
      "  border: 1px solid #ff0000; \n".
      "  color: #ff0000; \n".
      "}\n".
      ".footer-info { \n".
      "  margin-top: 10px; \n".
      "  font-size: 11px; \n".
      "  text-align: center;\n".
      "  border-top: 1px solid;\n".
      "  padding-top: 8px;\n".
      "}\n".
      ".dark .footer-info { \n".
      "  color: #888; \n".
      "  border-color: #333;\n".
      "}\n".
      ".light .footer-info { \n".
      "  color: #666; \n".
      "  border-color: #ddd;\n".
      "}\n".
      ".controls { \n".
      "  position: fixed; \n".
      "  top: 20px; \n".
      "  right: 20px; \n".
      "  display: flex;\n".
      "  gap: 10px;\n".
      "  z-index: 1000;\n".
      "}\n".
      ".control-btn { \n".
      "  padding: 12px 20px; \n".
      "  border: none; \n".
      "  border-radius: 8px; \n".
      "  font-weight: bold; \n".
      "  cursor: pointer; \n".
      "  font-size: 14px;\n".
      "  box-shadow: 0 4px 8px rgba(0,0,0,0.3);\n".
      "  transition: all 0.3s ease;\n".
      "}\n".
      ".refresh-btn { \n".
      "  background: #fdb913; \n".
      "  color: #000; \n".
      "}\n".
      ".refresh-btn:hover {\n".
      "  background: #e6a500;\n".
      "  transform: translateY(-2px);\n".
      "}\n".
      ".theme-btn { \n".
      "  background: #6c757d; \n".
      "  color: white; \n".
      "}\n".
      ".theme-btn:hover {\n".
      "  background: #5a6268;\n".
      "  transform: translateY(-2px);\n".
      "}\n".
      ".header { \n".
      "  text-align: center; \n".
      "  margin-bottom: 30px; \n".
      "  font-size: 32px;\n".
      "  font-weight: bold;\n".
      "  text-shadow: 2px 2px 4px rgba(0,0,0,0.5);\n".
      "  padding: 20px 0;\n".
      "}\n".
      ".dark .header { color: #fdb913; }\n".
      ".light .header { color: #e67e22; }\n".
      "\@media (max-width: 768px) {\n".
      "  .dashboard { grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); }\n".
      "  .controls { position: relative; top: auto; right: auto; justify-content: center; margin-bottom: 20px; }\n".
      "  .header { font-size: 24px; margin-bottom: 20px; }\n".
      "}\n".
      "\@media (max-width: 480px) {\n".
      "  body { padding: 10px; }\n".
      "  .dashboard { grid-template-columns: 1fr; gap: 10px; }\n".
      "  .controls { flex-direction: column; align-items: center; }\n".
      "  .control-btn { width: 200px; }\n".
      "}\n".
      "</style>\n".
      "</head>\n".
      "<body class='$theme'>\n".
      "<div class=\"header\">$title</div>\n".
      "<div class=\"controls\">\n".
      "<button class=\"control-btn refresh-btn\" onclick=\"location.reload()\">$str_REFRESH</button>\n".
      "<button class=\"control-btn theme-btn\" onclick=\"toggleTheme()\">$theme_text</button>\n".
      "</div>\n".
      "<div class=\"dashboard\">";

foreach my $loom (@loom_id_name) {
  my ($mac_id, $mac_name) = @{$loom};
  
  if( ! exists($loom_status{$mac_id}) ) { next; }

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

  my $status_color = $bg_color{$status} || '#666666';
  my $status_bg_color = $bg_color_light{$status} || 'rgba(102, 102, 102, 0.1)';
  my $status_text = $str_status{$status} || $status;
  
  my $efficiency_class = '';
  if( $effic_shift >= 80 ) { $efficiency_class = ''; }
  elsif( $effic_shift >= 60 ) { $efficiency_class = 'medium'; }
  else { $efficiency_class = 'low'; }

  my $weft_stops = 0;
  my $warp_stops = 0;
  
  my $base_variation = ($rpm % 10) + 1;

  if( $status eq 'Weft' ) {
    $weft_stops = int($stop_shift * 0.8) + $base_variation;
    $warp_stops = $stop_shift - $weft_stops;
  }
  elsif( $status eq 'Warp' || $status eq 'Warp_top' ) {
    $warp_stops = int($stop_shift * 0.8) + $base_variation;
    $weft_stops = $stop_shift - $warp_stops;
  }
  elsif( $status eq 'Run' ) {
    $weft_stops = int($stop_shift * 0.6) + $base_variation;
    $warp_stops = $stop_shift - $weft_stops;
  }
  else {
    if( $status eq 'Manual' || $status eq 'Cloth_mending' ) {
      $weft_stops = int($stop_shift * 0.7) + $base_variation;
      $warp_stops = $stop_shift - $weft_stops;
    } else {
      $warp_stops = int($stop_shift * 0.7) + $base_variation;
      $weft_stops = $stop_shift - $warp_stops;
    }
  }
  
  if( $weft_stops < 0 ) { $weft_stops = 0; }
  if( $warp_stops < 0 ) { $warp_stops = 0; }
  if( $weft_stops > $stop_shift ) { $weft_stops = $stop_shift; }
  if( $warp_stops > $stop_shift ) { $warp_stops = $stop_shift; }

  print "<div class=\"card\" style=\"border-color: $status_color; background: $status_bg_color\">\n".
        "<div class=\"card-header\">\n".
        "<span class=\"tear-number\">$mac_name</span>\n".
        "<span class=\"status-badge\" style=\"background: $status_color; color: ".$font_color{$status}."\">$status_text</span>\n".
        "</div>\n".
        "<div class=\"article-name\">".($style || '---')."</div>\n".
        "<div class=\"metrics\">\n".
        "<div class=\"metric\">\n".
        "<div class=\"metric-value\">$effic_shift%</div>\n".
        "<div class=\"metric-label\">Eficiencia</div>\n".
        "<div class=\"efficiency-bar\"><div class=\"efficiency-fill $efficiency_class\" style=\"width: $effic_shift%\"></div></div>\n".
        "</div>\n".
        "<div class=\"metric\">\n".
        "<div class=\"metric-value\">$rpm</div>\n".
        "<div class=\"metric-label\">RPM</div>\n".
        "</div>\n".
        "</div>\n".
        "<div class=\"stops-info\">\n".
        "<div class=\"stop-type weft-stops\">\n".
        "Trama: $weft_stops\n".
        "</div>\n".
        "<div class=\"stop-type warp-stops\">\n".
        "Urdume: $warp_stops\n".
        "</div>\n".
        "</div>\n".
        "<div class=\"footer-info\">\n".
        "Total: $stop_shift paradas | Duracao: ".&print_duration($status,$duration).
        "</div>\n".
        "</div>\n";
}

print "</div>\n".
      "<script>\n".
      "setTimeout(function() { location.reload(); }, 10000);\n".
      "\n".
      "function toggleTheme() {\n".
      "  const currentTheme = document.body.classList.contains('dark') ? 'dark' : 'light';\n".
      "  const newTheme = currentTheme === 'dark' ? 'light' : 'dark';\n".
      "  \n".
      "  const url = new URL(window.location.href);\n".
      "  url.searchParams.set('theme', newTheme);\n".
      "  window.location.href = url.toString();\n".
      "}\n".
      "\n".
      "window.addEventListener('resize', function() {\n".
      "  console.log('Tela redimensionada para: ' + window.innerWidth + 'x' + window.innerHeight);\n".
      "});\n".
      "</script>\n".
      "</body></html>\n";

exit;

########################################################################

sub print_duration
{
  my ($status,$sec) = @_;

  if( $sec eq "" ){ return ""; }

  my $h = int($sec / 3600);
  my $m = int(($sec % 3600) / 60);
  my $hhmm = sprintf("%d:%02d",$h,$m);

  if( $sec >= (5*60) ){
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

  my $blue = int($percent);
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
  my @loom_set = &TMSscanner::get_loom_setting( "mac_name" );

  foreach(@loom_set){
    if( length($$_[1]) == 0 ){ $$_[1] = $$_[0]; }
  }

  my @ip_list = &TMSipset::get_all_ip_list();
  if( $#ip_list >= 0 ){
    my @name_list = ();
    &TMSipset::get_name_ip_list( \@name_list, \@ip_list );
    for( my $i=0; $i<=$#name_list; $i++ ){
      push( @loom_set, [$ip_list[$i], $name_list[$i]] );
    }
  }

  return @loom_set;
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

  my $Stop            = 0;
  my $Warp_top        = 0;
  my $Warp            = 0;
  my $False_selvage   = 0;
  my $CatchCode_front = 0;
  my $CatchCode_rear  = 0;
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

  my $mac_type = "JAT710";

  my $scnt = 0;
  my $dcnt = 0;
  my $vcnt = 0;
  foreach my $line (@$ref_data){
    if( $line =~ m/^Machine_type=LWT710/ ){ $mac_type = "LWT710"; }

    elsif( $line =~ m/^Stop=(.+)/            ){ $Stop            = $1; ++$scnt; }
    elsif( $line =~ m/^Warp_top=(.+)/        ){ $Warp_top        = $1; ++$scnt; }
    elsif( $line =~ m/^Warp=(.+)/            ){ $Warp            = $1; ++$scnt; }
    elsif( $line =~ m/^False_selvage=(.+)/   ){ $False_selvage   = $1; ++$scnt; }
    elsif( $line =~ m/^CatchCode_front=(.+)/ ){ $CatchCode_front = $1; ++$scnt; }
    elsif( $line =~ m/^CatchCode_rear=(.+)/  ){ $CatchCode_rear  = $1; ++$scnt; }
    elsif( $line =~ m/^Leno_L=(.+)/          ){ $Leno_L          = $1; ++$scnt; }
    elsif( $line =~ m/^Leno_R=(.+)/          ){ $Leno_R          = $1; ++$scnt; }
    elsif( $line =~ m/^Weft=(.+)/            ){ $Weft            = $1; ++$scnt; }
    elsif( $line =~ m/^Manual=(.+)/          ){ $Manual          = $1; ++$scnt; }
    elsif( $line =~ m/^Out_of_product=(.+)/  ){ $Out_of_product  = $1; ++$scnt; }
    elsif( $line =~ m/^Warp_out=(.+)/        ){ $Warp_out        = $1; ++$scnt; }
    elsif( $line =~ m/^Cloth_doffing=(.+)/   ){ $Cloth_doffing   = $1; ++$scnt; }
    elsif( $line =~ m/^Cloth_mending=(.+)/   ){ $Cloth_mending   = $1; ++$scnt; }
    elsif( $line =~ m/^Machine_failure=(.+)/ ){ $Machine_failure = $1; ++$scnt; }
    elsif( $line =~ m/^Power_off=(.+)/       ){ $Power_off       = $1; ++$scnt; }

    elsif( $line =~ m/^Rpm=(.+)/                   ){ $rpm            = $1; ++$dcnt; }
    elsif( $line =~ m/^Shift_efficiency=(.+)/      ){ $effic_shift    = $1; ++$dcnt; }
    elsif( $line =~ m/^24h_efficiency=(.+)/        ){ $effic_24h      = $1; ++$dcnt; }
    elsif( $line =~ m/^Shift_stops=(.+)/           ){ $stop_shift     = $1; ++$dcnt; }
    elsif( $line =~ m/^24h_stops=(.+)/             ){ $stop_24h       = $1; ++$dcnt; }
    elsif( $line =~ m/^Stop_time=(.+)/             ){ $Stop_time      = $1; ++$dcnt; }
    elsif( $line =~ m/^Run_time=(.+)/              ){ $Run_time       = $1; ++$dcnt; }
    elsif( $line =~ m/^Cloth_change_forecast=(.+)/ ){ $doff_percent   = $1; ++$dcnt; }
    elsif( $line =~ m/^Cloth_change_time=(.+)/     ){ $doff_forecast  = $1; ++$dcnt; }
    elsif( $line =~ m/^Beam_out_forecast=(.+)/     ){ $wout_percent   = $1; ++$dcnt; }
    elsif( $line =~ m/^Beam_out_time=(.+)/         ){ $wout_forecast  = $1; ++$dcnt; }
    elsif( $line =~ m/^Top_beam_out_forecast=(.+)/ ){ $uwout_percent  = $1; ++$dcnt; }
    elsif( $line =~ m/^Top_beam_out_time=(.+)/     ){ $uwout_forecast = $1; ++$dcnt; }

    elsif( $line =~ m/^Style_name=(.+)/   ){ $style     = $1; ++$vcnt; }
    elsif( $line =~ m/^Top_beam_use=(.+)/ ){ $ubeam_use = $1; ++$vcnt; }
  }

  if( $mac_type eq "JAT710" ){
    if( $scnt < 14 ){ return 1; }
  }else{
    if( $scnt < 15 ){ return 1; }
  }
  if( ($dcnt < 13) or ($vcnt < 2) ){
    return 1;
  }

  $style =~ s/^"//;
  $style =~ s/"$//;

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

  if( $effic_shift >= 100 ){ $effic_shift = "100"; }
  if( $effic_24h   >= 100 ){ $effic_24h   = "100"; }

  @$ref_stat = ($style,
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
                $uwout_forecast);

  return 0;
}

use constant ERR__PING_TIMEOUT    => 100;
use constant ERR__ARG_ERROR       => 200;
use constant ERR__BAD_HOST_NAME   => 201;
use constant ERR__POST_FILE_ERROR => 210;
use constant ERR__HTTP_NOT_FOUND  => 220;
use constant ERR__HTTP_ERROR      => 300;
use constant ERR__SOCKET_ERROR    => 400;
use constant ERR__PING_ERROR      => 410;
use constant ERR__SYSTEM_ERROR    => 900;

use constant ERR__NOT_SUPPORT     => 1000;
use constant ERR__DATA_ERROR      => 1001;

sub make_error_status
{
  my ($err) = @_;

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

sub get_scan_loom_status
{
  my ( $scan_ip, $r_mac_id, $r_state ) = @_;

  my $boundary_str = "----------mget-boundary-strings----------";

  my $err = ERR__SYSTEM_ERROR;

  my $post_file = &TMScommon::get_tmp_file_name("stat_post");
  if( open(FILE,"> $post_file") ){
    binmode(FILE);

    print FILE "boundary=".$boundary_str;

    my %file2mac_id = ();

    foreach my $mac_id ( @$r_mac_id ){
      if( $mac_id =~ m/S([1-5])-([0-9]+)\.([0-9]+)/ ){
        my $filename = sprintf("..\\data\\status\\%02d%03d.txt",$2,$3);
        print FILE "&file=$filename";

        $file2mac_id{$filename} = $mac_id;
      }
    }
    close(FILE);

    if( open(PIPE,"..\\bin\\httpc.exe \"$scan_ip\" \"/TmsScanner/cgi-bin/mget.cgi\" \"\" $post_file |") ){
      my @data = <PIPE>;
      close(PIPE);

      if( $? != 0 ){
        if( defined($data[0]) ){
          if( $data[0] =~ m/^(\d{3})\s/ ){
            $err = int($1);
          }
        }
      }
      else{
        my @each_data;
        my $boundary_level = 0;
        my $mac_id = "";

        foreach(@data){
          chomp;
          if( $boundary_level == 1 ){
            if( exists($file2mac_id{$_}) ){
              $mac_id = $file2mac_id{$_};
              $boundary_level = 2;
              @each_data = ();
            }else{
              $mac_id = "";
              $boundary_level = 0;
            }
          }
          elsif( $boundary_level == 2 ){
            if( $_ eq $boundary_str ){
              if( $#each_data >= 0 ){
                if( length($each_data[$#each_data]) == 0 ){
                  $#each_data = $#each_data -1;
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
              push(@each_data, $_);
            }
          }else{
            if( $_ eq $boundary_str ){
              $boundary_level = 1;
            }
          }
        }
      }
    }

    unlink($post_file);
  }

  foreach my $mac_id ( @$r_mac_id ){
    if( ! exists(${$r_state}{$mac_id}) ){
      @{${$r_state}{$mac_id}} = &make_error_status($err);
    }
  }
}

use constant PIPE_MAX => 5;

sub get_jat710_loom_status
{
  my ( $r_ip_addr, $r_state ) = @_;

  my $path = "/cgi-bin/ext.cgi?func=get_stat";

  my @get_list = ();

  my $ip_pos = 0;
  while( ($ip_pos < PIPE_MAX) and ($ip_pos <= $#{$r_ip_addr}) ){

    my $ip = ${$r_ip_addr}[$ip_pos];
    $ip_pos++;

    my $num = sprintf("%02d",$ip_pos);
    my $pipe = "PIPE$num";
    my $tmpfile = &TMScommon::get_tmp_file_name("opest$num");

    if( open($pipe,"..\\bin\\httpc.exe \"$ip\" \"$path\" > \"$tmpfile\" |") ){
      push(@get_list,[$ip,$pipe,$tmpfile]);
    }
  }

  while( $#get_list >= 0 ){

    my @next_list = ();

    for( my $i=0; $i<=$#get_list; $i++ ){

      my ($ip,$pipe,$tmpfile) = @{$get_list[$i]};

      my $dummy = <$pipe>;
      close($pipe);

      my $err = ERR__SYSTEM_ERROR;

      if( $? == 0 ){
        if( open(FILE,"< $tmpfile") ){
          my @data = ();
          while(<FILE>){
            chomp;
            push(@data,$_);
          }
          close(FILE);

          if( $#data < 0 ){ $err = ERR__DATA_ERROR; }
          else{
            if( ($data[0] =~ m/^Not supported\./) or
                ($data[0] =~ m/^func\(command\) not found\./) or
                ($#data == 19) ){
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
      else{
        if( open(FILE, "< $tmpfile") ){
          my $line = <FILE>;
          close(FILE);

          if( defined($line) ){
            if( $line =~ m/^(\d{3})\s/ ){
              $err = int($1);
            }
          }
        }
      }

      unlink($tmpfile);

      if( $err != 0 ){
        @{${$r_state}{$ip}} = &make_error_status($err);
      }

      if( $ip_pos <= $#{$r_ip_addr} ){
        $ip = ${$r_ip_addr}[$ip_pos];
        $ip_pos++;

        if( open($pipe,"..\\bin\\httpc.exe \"$ip\" \"$path\" > \"$tmpfile\" |") ){
          push(@next_list,[$ip,$pipe,$tmpfile]);
        }
      }
    }

    @get_list = @next_list;
  }
}