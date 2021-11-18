<?php

use function PHPSTORM_META\type;

error_reporting(E_ALL);
ini_set("display_errors", 1);
ini_set("error_log", 'wp-multitool/err_log.php');


# Here we set the URL from the repo where MySQLDump, WP Cli, etc. scripts are stored
$config_url_mysqldump = "http://todorivanov.net/repo/mysqldump.tar.gz";
$cofnig_url_wpcli = "http://todorivanov.net/repo/wp-cli.tar.gz";

$runtime_path_root = "";
$runtime_path_wpconfig = "";
$runtime_path_wpcli = "";
$runtime_path_client_link = "wp-multitool/wp-cli/wp-cli.phar";
$runtime_db_settings = array();

function search_wp_config(){
    # Source: https://www.php.net/manual/en/function.scandir.php
    # Here we get a list of all the files and folders in the root dir of the script
    $dir_scan = scandir(__DIR__);
    foreach ($dir_scan as $item){
            # Here we check whether the list item matches the wp-config file
            if ($item == "wp-config.php"){
                # If a match is found we save it to the global $runtime_path_wpconfig and $runtime_path_root variables
                global $runtime_path_wpconfig;
                global $runtime_path_root;
                $runtime_path_wpconfig = __DIR__ . "/" . $item;
                $runtime_path_root = __DIR__;
            }
        }
}

function link_to_client($cid="", $wid=""){
    if ($cid == "" | $wid == ""){
        # If the parameters are empty we return an Err message
        $response = array(
            "Error" => "[HOST][API][Err][01]",
            "Message" =>  "Can't link the Client to the Host. Missing link parameters"
        );
        return json_encode($response);
    }else{
        # First we check whether the config folder exists
        $config_dir = 'wp-multitool/config';
        if (!file_exists($config_dir)){
            # And if doesn't exist we create it
            mkdir(($config_dir), 0755, true);
        }
        # Next we check whether the config.json file exists
        if (!file_exists($runtime_path_client_link)){
            # And if it doesn't then we create an empty file
            $empty_file = fopen($runtime_path_client_link, w);
            fclose($empty_file);
        }else{
            # Else we read the config.json file
            $read_file = json_decode(file_get_contents($runtime_path_client_link), true);
            # DEBUG: And then print the contents of the file
            foreach ($read_file as $key => $item){
                echo "Key: " . $key . " Value: " . $item;
            }

            # TODO: Next we should compare the "cid" and "wid" keys from the config.json file
            # With the cid and wid parameters received from the query paramaters
        }



        # Here we check if the WP Cli is already downloaded
    if (!file_exists($runtime_path_client_link)){
        # In case the file doesn't exist we download it from the repo URL
        if (file_put_contents('wp-multitool/' . $file_wpcli, file_get_contents($cofnig_url_wpcli))){
            # Here we decompress the .gz archive
            $file_wpcli_decompressed = new PharData('wp-multitool/' . $file_wpcli);
            $file_wpcli_decompressed -> decompress();
            # And next we extract the file from the archive
            $file_wpcli_extracted = new PharData('wp-multitool/' . $file_wpcli);
            $file_wpcli_extracted -> extractTo('wp-multitool/wp-cli');
            # TODO: Report wp-cli.phar location
    }
}


function recursiveChmod($path, $filePerm=0644, $dirPerm=0755) {
    # Source: https://gist.github.com/mikamboo/9205589

    // Check if the path exists
    if (!file_exists($path)) {
        return(false);
    }

    // See whether this is a file
    if (is_file($path)) {
        // Chmod the file with our given filepermissions
        chmod($path, $filePerm);

    // If this is a directory...
    } elseif (is_dir($path)) {
        // Then get an array of the contents
        $foldersAndFiles = scandir($path);

        // Remove "." and ".." from the list
        $entries = array_slice($foldersAndFiles, 2);

        // Parse every result...
        foreach ($entries as $entry) {
            // And call this function again recursively, with the same permissions
            recursiveChmod($path."/".$entry, $filePerm, $dirPerm);
        }

        // When we are done with the contents of the directory, we chmod the directory itself
        chmod($path, $dirPerm);
    }

    // Everything seemed to work out well, return true
    return(true);
}


#
#   Database functions
#
function db_get_settings(){
        search_wp_config();
        #Source: https://stackoverflow.com/questions/3686177/php-to-search-within-txt-file-and-echo-the-whole-line
        #Source: https://www.php.net/manual/en/function.preg-match-all.php
        #Source: https://www.oreilly.com/library/view/php-cookbook/1565926811/ch13s07.html
        global $runtime_path_wpconfig;
        global $runtime_db_settings;
        # Here we open and save the wp-config.php file into the $wpconfig_opened file
        $wpconfig_opened = file_get_contents($runtime_path_wpconfig);
        # Here we prepare a list of strings to be searched later
        $search_list = [ "DB_NAME", "DB_USER", "DB_PASSWORD", "DB_HOST" ];
        for ($i = 0; $i<count($search_list); $i++){
            # PHP IS A FUCKING STUPID LANGUAGE!!!!
            # WHY THE FUCK SHOULD THERE BE DELIMETERS AT THE START AND END OF REGEX?????
            # Source: https://stackoverflow.com/questions/27771852/preg-match-no-ending-delimiter
            # And the pattern we'll use to search for the data
            $pattern = '~\'(?<type>' . $search_list[$i]. ')\', ?\'(?<match>.*)\'~';
            # Here we check for the match
            if (preg_match_all( $pattern, $wpconfig_opened, $temp)){
                # PHP is fucking stupid ....
                $temp_type=$temp['type'][0];
                $temp_match=$temp['match'][0];
                # And then save the match and the type to the $runtime_db_settings associatve array
                $runtime_db_settings[$temp_type] = $temp_match;
            }
            else{
                # TODO: Report inablity to find DB settings -> could be a custom wp-config.php file
                $response = array("Error" => "[HOST][MySQL][Err][01]", "Data" => "Failed to retrieve DB settings");
                return json_encode($response);
            }
        }
}

function db_setup_mysqldump(){
    # Source: https://www.geeksforgeeks.org/download-file-from-url-using-php/
    # Here we declare that we'll be accessing the global $config_url_mysqldump variable
    global $config_url_mysqldump;
    # Here we get the name of the file from the URL
    $file_mysqldump = basename($config_url_mysqldump);
    # Source: https://stackoverflow.com/questions/2303372/create-a-folder-if-it-doesnt-already-exist
    # Here we make an empty directory:
    if (!file_exists('wp-multitool/mysqldump')){
        mkdir('wp-multitool/mysqldump', 0755, true);
    }
    # Here we check whether the mysqldump script is already downloaded
    if (!file_exists('wp-multitool/mysqldump.tar.gz') | !file_exists('wp-multitool/mysqldump.tar')){
        # Here we download the file from the URL
        if (file_put_contents( 'wp-multitool/' . $file_mysqldump, file_get_contents($config_url_mysqldump))){
            # Source: https://stackoverflow.com/questions/9416508/php-untar-gz-without-exec
            # Here we decompress the .gz archive
            $file_mysqldump_decompressed = new PharData('wp-multitool/' . $file_mysqldump);
            $file_mysqldump_decompressed -> decompress();
            # Here we extract the .tar archive
            $file_mysqldump_extracted = new PharData('wp-multitool/' . $file_mysqldump);
            $file_mysqldump_extracted -> extractTo('wp-multitool/mysqldump');
        }
        else{
            # TODO: Report inablity to download the MySQLDump script -> could be a connectivity problem
            $response = array("Error" => "[HOST][MySQL][Err][00]", "Data" => "Failed to generate backup");
            return json_encode($response);
        }
    }
    # If else the file is already downloaded
}

function db_generate_backup(){
    db_get_settings();
    db_setup_mysqldump();

    include 'wp-multitool/mysqldump/src/Ifsnop/Mysqldump/Mysqldump.php';
    global $runtime_db_settings;
    $temp_host = $runtime_db_settings['DB_HOST'];
    $temp_db = $runtime_db_settings['DB_NAME'];
    echo "Host: " . $temp_hos . "DB: " . $temp_db;
    $dump = new Ifsnop\Mysqldump\Mysqldump("mysql:host=$temp_host;dbname=$temp_db", $runtime_db_settings['DB_USER'], $runtime_db_settings['DB_PASSWORD']);
    if (!file_exists('wp-multitool/backups/mysql')){
        mkdir('wp-multitool/backups/mysql', 0755, true);
    }
    $date = date("Y-m-d-h-i");
    $dump->start('wp-multitool/backups/mysql/'. $runtime_db_settings['DB_NAME'] . '-' . $date . '.sql');

    # TODO: Report the name of the db.sql file that was generated
    $response = array("Info" => "[HOST][MySQL][Info][00]", "Data"  => "Generated DB backup");
    return json_encode($response);
}


#
#   File functions
#
function files_permission_fix(){
    # Here we find the doc root folder of the website using the 'search_wp_config' function
    search_wp_config();
    global $runtime_path_root;
    if (empty($runtime_path_root)){
        # TODO: Report that the global functions 'runtime_path_wpcli' and 'runtime_path_root' are empty
        $response = array("Error" => "[HOST][FILE][Err][00]", "Data" => "Failed to generate 'runtime_path_root'");
        print_r($response);
        #return json_encode($response);
    }
    else{
        $command = "find " . $runtime_path_root . " -type d -print0 | xargs -0 chmod 0755 && find " . $runtime_path_root . " -type f -print0 | xargs -0 chmod 0644;";
        # Here the variables are:
        # $command - the shell script that we're going to execute
        # $output - the result from successfully running the script
        # $return - the error code returned by the shell script, if there is such
        $result = exec($command, $output, $return);
        if ($return != 0){
            # TODO: Report that the execution of the command failed
            # In case the execution of the command failed
            echo $command;
            echo "DEBUG: " . $return;
            print_r($output);
        }
        else{
            http_response_code(200);
            echo json_encode($output);
        }
    }
}

function files_root_size_get($dir=""){
    # Source: https://stackoverflow.com/questions/478121/how-to-get-directory-size-in-php
    search_wp_config();
    global $runtime_path_root;

    # NOTE: This solution only applies to Linux hosting. Not sure if we should support Windows hosting at all.
    $io = popen('/usr/bin/du -sk ' . $runtime_path_root, 'r');
    $size = fgets($io, 4096);
    $size = substr($size, 0, strpos($size,"\t"));
    pclose($io);
    echo $size;
}

function files_root_archive(){

}

#
#   WordPress functions
#
function wp_setup_cli(){
    # Here we define the URL for the repo to WP Cli
    global $cofnig_url_wpcli;
    global $runtime_path_wpcli;
    global $runtime_path_root;
    # And get the name of the file from the repo
    $file_wpcli = basename($cofnig_url_wpcli);
    if (!file_exists('wp-multitool/wp-cli')){
        mkdir('wp-multitool/wp-cli', 0755, true);
    }
    # Here we check if the WP Cli is already downloaded
    if (!file_exists('wp-multitool/wp-cli/wp-cli.phar')){
        # In case the file doesn't exist we download it from the repo URL
        if (file_put_contents('wp-multitool/' . $file_wpcli, file_get_contents($cofnig_url_wpcli))){
            # Here we decompress the .gz archive
            $file_wpcli_decompressed = new PharData('wp-multitool/' . $file_wpcli);
            $file_wpcli_decompressed -> decompress();
            # And next we extract the file from the archive
            $file_wpcli_extracted = new PharData('wp-multitool/' . $file_wpcli);
            $file_wpcli_extracted -> extractTo('wp-multitool/wp-cli');
            # TODO: Report wp-cli.phar location
        }
        else{
            # TODO: Report inablity to download wp-cli
        }
    }
    else{
        # If the wp-cli.phar is already downloaded:
        $runtime_path_wpcli = $runtime_path_root . '/wp-multitool/wp-cli/wp-cli.phar';
    }

}

function wp_core_version_get(){
    # Here we find the doc root folder of the website using the 'search_wp_config' function
    search_wp_config();
    # Here we verify that the wp-cli is donwloaded within the 'wp-multitool' folder via the 'wp_setup_cli' function
    wp_setup_cli();
    # Then we specify the global variables that were defined with the previous two functions
    global $runtime_path_wpcli;
    global $runtime_path_root;
    if (empty($runtime_path_wpcli) || empty($runtime_path_root)){
        # TODO: Report that the global functions 'runtime_path_wpcli' and 'runtime_path_root' are empty
        $response = array("Error" => "[ERR][WP][00]", "Data" => "Failed to generate 'runtime_path_wpcli' or 'runtime_path_root'");
        return json_encode($response);
    }
    else{
        $command = "php " . $runtime_path_wpcli . " core version --path=" . $runtime_path_root;
        # Here the variables are:
        # $command - the shell script that we're going to execute
        # $output - the result from successfully running the script
        # $return - the error code returned by the shell script, if there is such
        $result = exec($command, $output, $return);
        if ($return != 0){
            # TODO: Report that the execution of the command failed
            # In case the execution of the command failed
            echo "DEBUG: " . $output . $return;
        }
        else{
            http_response_code(200);
            echo json_encode($output);
        }
    }
}


function wp_core_reset(){
    # Here we verify that the wp-cli is donwloaded within the 'wp-multitool' folder via the 'wp_setup_cli' function
    search_wp_config();
    # Then we specify the global variables that were defined with the previous two functions
    wp_setup_cli();
    # Then we specify the global variables that were defined with the previous two functions
    global $runtime_path_wpcli;
    global $runtime_path_root;
    if (empty($runtime_path_wpcli) || empty($runtime_path_root)){
        # TODO: Report that the global functions 'runtime_path_wpcli' and 'runtime_path_root' are empty
        $response = array("Error" => "[ERR][WP][00]", "Data" => "Failed to generate 'runtime_path_wpcli' or 'runtime_path_root'");
        return json_encode($response);
    }
    else{
        $command1 = "php " . $runtime_path_wpcli . " core version";
        $result1 = exec($command1, $output1, $return1);
        if ($return1 != 0 ){
            # TODO: Report that the execution of the command failed
            # In case the execution of the command failed
            echo "DEBUG: " .  $output1 . $return1;
        }else{
            # TODO: Add regex verification to '$output1[0]' to ensure that it passes WP version number
            $command2 = "php " . $runtime_path_wpcli . " core download --force --version=" . $output1[0];
            $result2 = exec($command2, $output2, $return2);
            if ($return2 != 0){
                # TODO: Report that the execution of the command failed
                # In case the execution of the command failed
                echo "DEBUG: " . $output2 . $return2;
            }
            else{
                http_response_code(200);
                echo json_encode($output2);
            }
        }
    }
}


function wp_checksum_verify(){
    # Here we verify that the wp-cli is donwloaded within the 'wp-multitool' folder via the 'wp_setup_cli' function
    search_wp_config();
    # Then we specify the global variables that were defined with the previous two functions
    wp_setup_cli();
    # Then we specify the global variables that were defined with the previous two functions
    global $runtime_path_wpcli;
    global $runtime_path_root;
    if (empty($runtime_path_wpcli) || empty($runtime_path_root)){
        # TODO: Report that the global functions 'runtime_path_wpcli' and 'runtime_path_root' are empty
        $response = array("Error" => "[ERR][WP][00]", "Data" => "Failed to generate 'runtime_path_wpcli' or 'runtime_path_root'");
        return json_encode($response);
    }
    else{
        $command = "php " . $runtime_path_wpcli . " core verify-checksums";
        $result = exec($command, $output, $return);
        if ($return != 0 ){
            # TODO: Report that the execution of the command failed
            # In case the execution of the command failed
            echo "DEBUG: " . $output . $return;
        }
        else{
            http_response_code(200);
            echo json_encode($output);
        }
    }

}


function wp_plugin_list(){
    # Here we find the doc root folder of the website using the 'search_wp_config' function
    search_wp_config();
    # Here we verify that the wp-cli is donwloaded within the 'wp-multitool' folder via the 'wp_setup_cli' function
    wp_setup_cli();
    # Then we specify the global variables that were defined with the previous two functions
    global $runtime_path_wpcli;
    global $runtime_path_root;
    if (empty($runtime_path_wpcli) || empty($runtime_path_root)){
        # TODO: Report that the global functions 'runtime_path_wpcli' and/or 'runtime_path_root' are empty
        $response = array("Error" => "[ERR][WP][01]", "Data" => "Failed to generate 'runtime_path_wpcli' or 'runtime_path_root'",);
        return json_encode($response);
    }
    else{
        $command = "php " . $runtime_path_wpcli . " plugin list --path=" . $runtime_path_root;
        $result = exec($command, $output, $return);
        if ($return != 0){
            # TODO: Report that the execution of the command failed
            # In case the execution of the command failed
            $response = array("Error" => "[HOST][ERR][WP][02]", "Data" => "Failed to execute command: [" . $command . "]",
                                "Output: " => $output);
            echo $response;
        }
        else{
            http_response_code(200);
            echo json_encode($output);
        }
    }
}

function wp_plugin_update($plugin_name){
    # IMPORTANT!!!!!
    # The web-server must have sufficient permissions to the wp-content folder and for PHP processes it spawns
    # Otherwise the script won't be able to download the theme files into the wp-content folder

    # Here we find the doc root folder of the website using the 'search_wp_config' function
    search_wp_config();
    # Here we verify that the wp-cli is donwloaded within the 'wp-multitool' folder via the 'wp_setup_cli' function
    wp_setup_cli();
    # Then we specify the global variables that were defined with the previous two functions
    global $runtime_path_wpcli;
    global $runtime_path_root;
    if (empty($runtime_path_wpcli) || empty($runtime_path_root)){
        # TODO: Report that the global functions 'runtime_path_wpcli' and/or 'runtime_path_root' are empty
        $response = array("Error" => "[HOST][ERR][WP][01]", "Data" => "Failed to generate 'runtime_path_wpcli' or 'runtime_path_root'");
        return json_encode($response);
    }
    else{
        $command = "php " . $runtime_path_wpcli . " plugin update " . $plugin_name . " --path=" . $runtime_path_root;
        # This is not pretty but the WP Cli won't properly update the plugin due to permissions/onwership
        recursiveChmod($runtime_path_root . "/wp-content", 0777, 0777);
        $result = exec($command, $output, $return);
        # So after completing the update we reset the permissions
        # This may have to be changed later if we find that the App can complete the update on most hosts or what permissions it needs
        recursiveChmod($runtime_path_root . "/wp-content", 0644, 0755);
        if ($return != 0){
            # TODO: Report that the global functions 'runtime_path_wpcli' and/or 'runtime_path_root' are empty
            $response = array("Error" => "[HOST][ERR][WP][02]", "Data" => "Failed to execute command: [" . $command . "]",
                                    "Output: " => $output);
            echo json_encode($response);
        }else{
            http_response_code(200);
            echo json_encode($output);
        }
    }
}


function wp_plugin_deactivate($plugin_name){
    # TODO: Extend this function so that it can also accept an array as parameter
    # And if so, disable all plugins that are listed within the array

    # Here we find the doc root folder of the website using the 'search_wp_config' function
    search_wp_config();
    # Here we verify that the wp-cli is donwloaded within the 'wp-multitool' folder via the 'wp_setup_cli' function
    wp_setup_cli();
    # Then we specify the global variables that were defined with the previous two functions
    global $runtime_path_wpcli;
    global $runtime_path_root;
    if (empty($runtime_path_wpcli) || empty($runtime_path_root)){
        # TODO: Report that the global functions 'runtime_path_wpcli' and/or 'runtime_path_root' are empty
        $response = array("Error" => "[HOST][ERR][WP][01]", "Data" => "Failed to generate 'runtime_path_wpcli' or 'runtime_path_root'");
        return json_encode($response);
    }
    else{
        $command = "php " . $runtime_path_wpcli . " plugin deactivate " . $plugin_name . " --path=" . $runtime_path_root;
        $response = exec ($command, $output, $return);
        if ($return != 0 ){
            # TODO: Report that the global functions 'runtime_path_wpcli' and/or 'runtime_path_root' are empty
            print_r($output);
            $response = array("Error" => "[HOST][ERR][WP][02]", "Data" => "Failed to execute command: [" . $command . "]",
                                    "Output: " => $output);
            echo json_encode($output);
        }else{
            http_response_code(200);
            echo json_encode($output);
        }
    }
}


function wp_plugin_activate($plugin_name){
    # TODO: Extend this function so that it can also accept an array as parameter
    # And if so, disable all plugins that are listed within the array

    # Here we find the doc root folder of the website using the 'search_wp_config' function
    search_wp_config();
    # Here we verify that the wp-cli is donwloaded within the 'wp-multitool' folder via the 'wp_setup_cli' function
    wp_setup_cli();
    # Then we specify the global variables that were defined with the previous two functions
    global $runtime_path_wpcli;
    global $runtime_path_root;
    if (empty($runtime_path_wpcli) || empty($runtime_path_root)){
        # TODO: Report that the global functions 'runtime_path_wpcli' and/or 'runtime_path_root' are empty
        $response = array("Error" => "[HOST][ERR][WP][01]", "Data" => "Failed to generate 'runtime_path_wpcli' or 'runtime_path_root'");
        echo json_encode($response);
    }
    else{
        $command = "php " . $runtime_path_wpcli . " plugin activate " . $plugin_name . " --path=" . $runtime_path_root;
        $response = exec ($command, $output, $return);
        if ($return != 0 ){
            # TODO: Report that the global functions 'runtime_path_wpcli' and/or 'runtime_path_root' are empty
            print_r($output);
            $response = array("Error" => "[HOST][ERR][WP][02]", "Data" => "Failed to execute command: [" . $command . "]",
                                    "Output: " => $output);
            echo json_encode($output);
        }else{
            http_response_code(200);
            echo json_encode($output);
        }
    }
}


function wp_theme_list(){
    # Here we find the doc root folder of the website using the 'search_wp_config' function
    search_wp_config();
    # Here we verify that the wp-cli is donwloaded within the 'wp-multitool' folder via the 'wp_setup_cli' function
    wp_setup_cli();
    # Then we specify the global variables that were defined with the previous two functions
    global $runtime_path_wpcli;
    global $runtime_path_root;
    if (empty($runtime_path_wpcli) || empty($runtime_path_root)){
        # TODO: Report that the global functions 'runtime_path_wpcli' and/or 'runtime_path_root' are empty
        $response = array("Error" => "[ERR][WP][01]", "Data" => "Failed to generate 'runtime_path_wpcli' or 'runtime_path_root'");
        return json_encode($response);
    }
    else{
        $command = "php " . $runtime_path_wpcli . " theme list --path=" . $runtime_path_root;
        $result = exec($command, $output, $return);
        if ($return != 0){
            # TODO: Report that the execution of the command failed
            # In case the execution of the command failed
            echo "DEBUG: " . $output . $return;
        }
        else{
            http_response_code(200);
            echo json_encode($output);
        }
    }
}

function wp_theme_update($theme_name){
    # IMPORTANT!!!!!
    # The web-server must have sufficient permissions to the wp-content folder and for PHP processes it spawns
    # Otherwise the script won't be able to download the theme files into the wp-content folder


    # Here we find the doc root folder of the website using the 'search_wp_config' function
    search_wp_config();
    # Here we verify that the wp-cli is donwloaded within the 'wp-multitool' folder via the 'wp_setup_cli' function
    wp_setup_cli();
    # Then we specify the global variables that were defined with the previous two functions
    global $runtime_path_wpcli;
    global $runtime_path_root;
    if (empty($runtime_path_wpcli) || empty($runtime_path_root)){
        # TODO: Report that the global functions 'runtime_path_wpcli' and/or 'runtime_path_root' are empty
        $response = array("Error" => "[HOST][ERR][WP][01]", "Data" => "Failed to generate 'runtime_path_wpcli' or 'runtime_path_root'");
        return json_encode($response);
    }
    else{
        $command = "php " . $runtime_path_wpcli . " theme update " . $theme_name . " --path=" . $runtime_path_root;
        # This is not pretty but the WP Cli won't properly update the plugin due to permissions/onwership
        recursiveChmod($runtime_path_root . "/wp-content", 0777, 0777);
        $result = exec($command, $output, $return);
        # So after completing the update we reset the permissions
        # This may have to be changed later if we find that the App can complete the update on most hosts or what permissions it needs
        recursiveChmod($runtime_path_root . "/wp-content", 0644, 0755);
        if ($return != 0){
            # TODO: Report that the global functions 'runtime_path_wpcli' and/or 'runtime_path_root' are empty
            print_r($output);
            $response = array("Error" => "[HOST][ERR][WP][02]", "Data" => "Failed to execute command: [" . $command . "]",
                                    "Output: " => $output);
            echo json_encode($response);
        }else{
            http_response_code(200);
            echo json_encode($output);
        }
    }
}

function wp_theme_deactivate($theme_name){
    # Here we find the doc root folder of the website using the 'search_wp_config' function
    search_wp_config();
    # Here we verify that the wp-cli is donwloaded within the 'wp-multitool' folder via the 'wp_setup_cli' function
    wp_setup_cli();
    # Then we specify the global variables that were defined with the previous two functions
    global $runtime_path_wpcli;
    global $runtime_path_root;
    if (empty($runtime_path_wpcli) || empty($runtime_path_root)){
        # TODO: Report that the global functions 'runtime_path_wpcli' and/or 'runtime_path_root' are empty
        $response = array("Error" => "[HOST][ERR][WP][01]", "Data" => "Failed to generate 'runtime_path_wpcli' or 'runtime_path_root'");
        return json_encode($response);
    }
    else{
        $command = "php " . $runtime_path_wpcli . " theme deactivate " . $theme_name . " --path=" . $runtime_path_root;
        $response = exec ($command, $output, $return);
        if ($return != 0 ){
            # TODO: Report that the global functions 'runtime_path_wpcli' and/or 'runtime_path_root' are empty
            print_r($output);
            $response = array("Error" => "[HOST][ERR][WP][02]", "Data" => "Failed to execute command: [" . $command . "]",
                                    "Output: " => $output);
            echo json_encode($output);
        }else{
            http_response_code(200);
            echo json_encode($output);
        }
    }
}

function wp_cache_flush(){
    # Here we find the doc root folder of the website using the 'search_wp_config' function
    search_wp_config();
    # Here we verify that the wp-cli is donwloaded within the 'wp-multitool' folder via the 'wp_setup_cli' function
    wp_setup_cli();
    # Then we specify the global variables that were defined with the previous two functions
    global $runtime_path_wpcli;
    global $runtime_path_root;
    if (empty($runtime_path_wpcli) || empty($runtime_path_root)){
        # TODO: Report that the global functions 'runtime_path_wpcli' and/or 'runtime_path_root' are empty
        $response = array("Error" => "[ERR][WP][01]", "Data" => "Failed to generate 'runtime_path_wpcli' or 'runtime_path_root'");
        return json_encode($response);
    }
    else{
        $command = "php " . $runtime_path_wpcli . " cache flush --path=" . $runtime_path_root;
        $result = exec($command, $output, $return);
        if ($return != 0){
            # TODO: Report that the execution of the command failed
            # In case the execution of the command failed
            echo "DEBUG: " . $output . $return;
        }
        else{
            http_response_code(200);
            echo json_encode($output);
        }
    }
}

#
#   Routing
#
$options_file = array(
    "backup" => "files_root_archive",
    "size" => "files_root_size_get",
    "permissions" => "files_permission_fix"
);
$options_db = array(
    "setup" => "db_setup_mysqldump",
    "settings" => "db_get_settings",
    "export" => "db_generate_backup"
);
$options_wp_core = array(
    "version" => "wp_core_version_get",
    "reset" => "wp_core_reset"
);
$options_wp_plugin = array(
    "list" => "wp_plugin_list",
    "update" => "wp_plugin_update",
    "enable" => "wp_plugin_activate",
    "disable" => "wp_plugin_deactivate"
);
$options_wp_theme = array(
    "list" => "wp_theme_list",
    "update" => "wp_theme_update",
    "disable" => "wp_theme_deactivate"
);
$options_wp_other = array(

);


$req_dict = array(
    "file" => $options_file,
    "db" => $options_db,
    "wp-core" => $options_wp_core,
    "wp-plugin" => $options_wp_plugin,
    "wp-theme" => $options_wp_theme,
    "wp-other" => $options_wp_other
);

# We expect to receive the type, option and data strings via query parameters. Therefore the URL should look like this:
# http://domain.com/wp-multitool.php?type=wp_core&option=reset

$received_type = $_GET['type'];
$received_option = $_GET['option'];
$received_data = $_GET['data'];
$received_cid = $_GET['cid'];

# Source: https://www.geeksforgeeks.org/how-to-call-php-function-from-string-stored-in-a-variable/
# First we list each available request type:
foreach ($req_dict as $req_key => $req_dict_element){
    # Then we check if the provided request type matches one of the available ones
    if ($req_key == $received_type){
        # If it does we then create a reference to the matched type
        $req_ref = $req_dict[$req_key];
        # Then we list all available options under the matched request type
        foreach ($req_ref as $opt_key => $req_options_element){
            # And if we find a match
            if ($opt_key == $received_option){
                # We then create a reference to the matched option
                $option_ref = $req_ref[$opt_key];
                # If there's provided data
                if (isset($received_data)){
                    $option_ref($received_data);
                }
                # And if no data is provided we simply execute the function
                else{
                    $option_ref();
                }
            }
        }
    }
}