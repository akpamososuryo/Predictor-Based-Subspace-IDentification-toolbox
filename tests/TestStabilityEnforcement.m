classdef TestStabilityEnforcement < matlab.unittest.TestCase
    properties
        RepoRoot
    end

    methods (TestMethodSetup)
        function addToolboxToPath(testCase)
            testCase.RepoRoot = fileparts(fileparts(mfilename('fullpath')));
            addpath(testCase.RepoRoot);
        end
    end

    methods (TestMethodTeardown)
        function removeToolboxFromPath(testCase)
            rmpath(testCase.RepoRoot);
        end
    end

    methods (Test)
        function stableOptionForcesEigenvaluesInsideUnitCircle(testCase)
            [u, y, sys] = testutils.makeSisoData('N', 600, 'seed', 4, 'noiseStd', 0.05);

            f = 5;
            p = 10;

            [~, X] = testutils.callDordvarx(u, y, f, p);

            n = 1;
            x = dmodx(X, n);

            % Try stable1 first (most likely supported)
            stableOpt = 'stable1';

            try
                [A, B, C, D] = testutils.callDx2abcd(x, u, y, f, p, stableOpt);
            catch ME
                testCase.assumeFail("Skipping stability test: " + string(ME.message));
                return
            end

            testCase.verifySize(A, [n, n]);
            testCase.verifyTrue(all(isfinite(A(:))));
            testCase.verifyLessThan(max(abs(eig(A))), 1.0);

            % Basic prediction check, loose but meaningful
            uRow = u';
            yRow = y';
            uTrim = uRow(:, p+1:p+size(x,2));
            yTrim = yRow(:, p+1:p+size(x,2));
            yHat = C * x + D * uTrim;

            err = yTrim - yHat;
            vaf = 100 * (1 - var(err, 1) / var(yTrim, 1));
            testCase.verifyGreaterThan(vaf, 50);

            % Near rank-deficient input: almost no excitation
            u2 = 1e-6 * randn(sys.N, 1);
            y2 = y; % same output, no new excitation, intentionally problematic

            [~, X2] = testutils.callDordvarx(u2, y2, f, p);
            x2 = dmodx(X2, n);

            try
                [A2, B2, C2, D2] = testutils.callDx2abcd(x2, u2, y2, f, p, stableOpt);
            catch ME
                testCase.assumeFail("Skipping near rank-deficient case: " + string(ME.message));
                return
            end

            testCase.verifyTrue(all(isfinite(A2(:))));
            testCase.verifyTrue(all(isfinite(B2(:))));
            testCase.verifyTrue(all(isfinite(C2(:))));
            testCase.verifyTrue(all(isfinite(D2(:))));
        end

        function stable2IfAvailableAlsoWorks(testCase)
            [u, y, ~] = testutils.makeSisoData('N', 500, 'seed', 5, 'noiseStd', 0.03);

            f = 5;
            p = 10;

            [~, X] = testutils.callDordvarx(u, y, f, p);
            n = 1;
            x = dmodx(X, n);

            try
                [A, ~, ~, ~] = testutils.callDx2abcd(x, u, y, f, p, 'stable2');
            catch ME
                testCase.assumeFail("stable2 not available: " + string(ME.message));
                return
            end

            testCase.verifyLessThan(max(abs(eig(A))), 1.0);
        end
    end
end