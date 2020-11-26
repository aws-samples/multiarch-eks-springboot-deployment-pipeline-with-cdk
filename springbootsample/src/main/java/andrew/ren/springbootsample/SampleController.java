package andrew.ren.springbootsample;

import java.lang.StringBuilder;
import java.time.Duration;
import javax.annotation.PostConstruct; 

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.json.simple.JSONObject;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.ResponseBody;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.jdbc.datasource.DriverManagerDataSource;

import redis.clients.jedis.Jedis;
import redis.clients.jedis.JedisPool;
import redis.clients.jedis.JedisPoolConfig;

@RestController
public class SampleController {

	@Value("${springbootsample.redis.host}")
    private String redis_host;
    
    @Value("${springbootsample.redis.port}")
    private int redis_port;
    
    @Value("${node}")
    private String node;
    
    @Value("${spring.datasource.url}")
    private String rds_url;
    
    @Value("${spring.datasource.username}")
    private String rds_username;
    
    @Value("${spring.datasource.driver-class-name}")
    private String rds_driver;
    
    
    Logger logger = LoggerFactory.getLogger(SampleController.class);
    
	
	@RequestMapping("/")
	@ResponseBody
	public String home() {
		JSONObject output = new JSONObject();
		
		output.put("Node Name", node);
		output.put("Redis Test", jedisTest());
		output.put("RDS Test", rdsTest());
		
        return output.toString();
	}
	
	private String jedisTest() {
		try {
		    JedisPoolConfig poolConfig = new JedisPoolConfig();
		    JedisPool pool = new JedisPool(poolConfig, redis_host, redis_port);
		    Jedis jedis = pool.getResource();
		    jedis.set("test", "value");
		    if (jedis.get("test").equals("value"))
		        return "passed";
		    else
		        return "failed";
	    }catch(Exception e){
	        return "failed";
	    }
		
	}
	
	private String rdsTest() {
		try {
			DriverManagerDataSource dataSource = new DriverManagerDataSource();
			dataSource.setDriverClassName(rds_driver);
			dataSource.setUrl(rds_url);
			dataSource.setUsername(rds_username);
			JdbcTemplate jdbcTemplate = new JdbcTemplate(dataSource);
			
		    jdbcTemplate.execute("CREATE DATABASE IF NOT EXISTS test");
		    StringBuilder sb = new StringBuilder();
		    sb.append("CREATE TABLE IF NOT EXISTS test.user (id int (10) unsigned NOT NULL AUTO_INCREMENT,\n")
		        .append("name varchar (64) NOT NULL DEFAULT '',\n")
		        .append("PRIMARY KEY (ID));\n");
		    jdbcTemplate.execute(sb.toString());
		    jdbcTemplate.update("REPLACE INTO test.user(id, name) VALUES(1, 'test')");
		    Integer count = jdbcTemplate.queryForObject("SELECT count(*) FROM test.user", Integer.class);
		    if (count == 1)
	        	return "passed";
	        else
	        	return "failed";
		}catch(Exception e){
	        return "failed";
	    }
	}
}
