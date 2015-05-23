var MemoryFileSystem = require("memory-fs");
var should = require("should");

describe("memory-filesystem", function() {
	var fileSystem;

	beforeEach(function() {
		fileSystem = new MemoryFileSystem({
			"": true,
			a: {
				"": true,
				index: new Buffer("1"), // /a/index
				dir: {
					"": true,
					index: new Buffer("2") // /a/dir/index
				}
			},
			"C:": {
				"": true,
				a: {
					"": true,
					index: new Buffer("3"),  // C:\files\index
					dir: {
						"": true,
						index: new Buffer("4")  // C:\files\a\index
					}
				}
			}
		});
	});

	describe("unix", function() {
		it("should stat stuff", function() {
			fileSystem.statSync("/a").isDirectory().should.be.eql(true);
			fileSystem.statSync("/a").isFile().should.be.eql(false);
			fileSystem.statSync("/a/index").isDirectory().should.be.eql(false);
			fileSystem.statSync("/a/index").isFile().should.be.eql(true);
			fileSystem.statSync("/a/dir").isDirectory().should.be.eql(true);
			fileSystem.statSync("/a/dir").isFile().should.be.eql(false);
			fileSystem.statSync("/a/dir/index").isDirectory().should.be.eql(false);
			fileSystem.statSync("/a/dir/index").isFile().should.be.eql(true);
		});
		it("should readdir directories", function() {
			fileSystem.readdirSync("/a").should.be.eql(["index", "dir"]);
			fileSystem.readdirSync("/a/dir").should.be.eql(["index"]);
		});
		it("should readdir directories", function() {
			fileSystem.readFileSync("/a/index", "utf-8").should.be.eql("1");
			fileSystem.readFileSync("/a/dir/index", "utf-8").should.be.eql("2");
		});
		it("should also accept multi slashs", function() {
			fileSystem.statSync("/a///dir//index").isFile().should.be.eql(true);
		});
	});

	describe("windows", function() {
		it("should stat stuff", function() {
			fileSystem.statSync("C:\\a").isDirectory().should.be.eql(true);
			fileSystem.statSync("C:\\a").isFile().should.be.eql(false);
			fileSystem.statSync("C:\\a\\index").isDirectory().should.be.eql(false);
			fileSystem.statSync("C:\\a\\index").isFile().should.be.eql(true);
			fileSystem.statSync("C:\\a\\dir").isDirectory().should.be.eql(true);
			fileSystem.statSync("C:\\a\\dir").isFile().should.be.eql(false);
			fileSystem.statSync("C:\\a\\dir\\index").isDirectory().should.be.eql(false);
			fileSystem.statSync("C:\\a\\dir\\index").isFile().should.be.eql(true);
		});
		it("should readdir directories", function() {
			fileSystem.readdirSync("C:\\a").should.be.eql(["index", "dir"]);
			fileSystem.readdirSync("C:\\a\\dir").should.be.eql(["index"]);
		});
		it("should readdir directories", function() {
			fileSystem.readFileSync("C:\\a\\index", "utf-8").should.be.eql("3");
			fileSystem.readFileSync("C:\\a\\dir\\index", "utf-8").should.be.eql("4");
		});
		it("should also accept multi slashs", function() {
			fileSystem.statSync("C:\\\\a\\\\\\dir\\\\index").isFile().should.be.eql(true);
		});
		it("should also accept a normal slash", function() {
			fileSystem.statSync("C:\\a\\dir/index").isFile().should.be.eql(true);
			fileSystem.statSync("C:\\a\\dir\\index").isFile().should.be.eql(true);
			fileSystem.statSync("C:\\a/dir/index").isFile().should.be.eql(true);
			fileSystem.statSync("C:\\a/dir\\index").isFile().should.be.eql(true);
		});
	});
});